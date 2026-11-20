// ==UserScript==
// @name         Saby Dialog → Wiki Ingest
// @namespace    saby.local
// @version      0.2.1
// @description  Кнопка на карточке диалога dev.saby.ru: выкачивает диалог в markdown и запускает сессию opencode с ингестом в вики
// @author       aa.timoshenko
// @match        https://dev.saby.ru/*
// @connect      127.0.0.1
// @grant        GM_xmlhttpRequest
// @grant        GM_openInTab
// @grant        unsafeWindow
// @noframes
// ==/UserScript==

(function () {
  'use strict';

  // === Настройки ===
  const OC_PORT = 28894;                            // порт opencode serve (opencode.exe serve --service)
  const OC_PASS = 'cpP4YXNVnq-yWVcbDpAMs_vmxOtAYrGVAqYsTVVpO0Y'; // ~/.config/opencode/service.json -> password
  const VAULT_DIR = 'C:\\Users\\aa.timoshenko\\PycharmProjects\\claude-obsidian\\wiki';
  const AGENT = 'build';
  const MODEL = { id: 'gpt-6.1-terra', providerID: 'openai', variant: 'medium' }; // GPT Terra Medium
  const BTN_CLASS = 'tm-saby-ingest-btn';

  const OC = 'http://127.0.0.1:' + OC_PORT;
  const AUTH = 'Basic ' + btoa('opencode:' + OC_PASS);
  const WEB_PREFIX = '/server/' + btoa(OC).replace(/=+$/, '');

  // === 1. Хук в контексте страницы: ловим theme_id открытого диалога из Message.List ===
  // (userscript работает в изолированном мире, поэтому хук внедряем script-тегом в контекст страницы)
  const hook = document.createElement('script');
  hook.textContent = '(' + function () {
    function tryCapture(body) {
      try {
        if (typeof body !== 'string' || body.indexOf('Message.List') === -1) return;
        var req = JSON.parse(body);
        var f = req.params && req.params['Фильтр'];
        if (!f) return;
        var idx = -1;
        for (var i = 0; i < (f.s || []).length; i++) {
          if (f.s[i].n === 'fromTheme') { idx = i; break; }
        }
        if (idx === -1) return;
        var v = f.d[idx];
        if (typeof v === 'string' && v.length > 30) {
          window.__sabyIngestTheme = { id: v, ts: Date.now() };
        }
      } catch (e) { /* не наш запрос */ }
    }
    var origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function (body) {
      tryCapture(body);
      return origSend.apply(this, arguments);
    };
    var origFetch = window.fetch;
    window.fetch = function (url, opts) {
      if (opts && opts.body) tryCapture(opts.body);
      return origFetch.apply(this, arguments);
    };
  } + ')()';
  document.documentElement.appendChild(hook);
  hook.remove();

  // === 2. Кнопка в шапке открытого диалога ===
  const observer = new MutationObserver(debounce(addButtons, 300));
  observer.observe(document.body, { childList: true, subtree: true });

  function debounce(fn, ms) {
    let t = null;
    return function () { clearTimeout(t); t = setTimeout(fn, ms); };
  }

  function addButtons() {
    document.querySelectorAll('.msg-ThemeView').forEach(panel => {
      if (panel.querySelector('.' + BTN_CLASS)) return;
      const actions = panel.querySelector('.msg-ThemeView__actions.msg-header-layout__actions');
      if (!actions) return;
      // кнопка собрана на родных классах Wasaby — выглядит как соседние иконки в шапке
      const btn = document.createElement('span');
      btn.className = BTN_CLASS +
        ' controls-BaseButton controls-Button_clickable controls-Button_bg-same controls-button-style controls-button_ghost-style';
      btn.setAttribute('data-cursor', 'pointer');
      btn.title = 'Выкачать диалог в markdown и запустить ингест в вики (opencode)';
      const wrap = document.createElement('span');
      wrap.className = 'controls-BaseButton__wrapper controls-Button__wrapper_viewMode-ghost controls-BaseButton__wrapper_caption-overflow';
      const icon = document.createElement('span');
      icon.className = 'controls-icon_size-m controls-BaseButton__icon icon-Download controls-icon';
      icon.style.color = '';
      wrap.appendChild(icon);
      btn.appendChild(wrap);
      btn.addEventListener('click', ev => {
        ev.preventDefault();
        ev.stopPropagation();
        onIngest(btn, panel);
      });
      actions.appendChild(btn);
    });
  }

  // === 3. Выкачивание диалога + запуск сессии opencode ===
  async function onIngest(btn, panel) {
    const icon = btn.querySelector('.controls-icon');
    const setStatus = (title, color) => {
      btn.title = title;
      if (icon) icon.style.color = color || '';
    };
    try {
      const theme = unsafeWindow.__sabyIngestTheme;
      if (!theme) {
        setStatus('Не поймал theme_id — закрой и открой диалог заново', '#ff8080');
        setTimeout(() => resetBtn(btn), 4000);
        return;
      }
      setStatus('⏳ Выкачиваю диалог…', '#ffd666');
      const md = await getMarkdown(theme.id);

      const title = guessTitle(panel, theme.id);
      setStatus('⏳ Создаю сессию opencode…', '#ffd666');
      const created = await ocRequest('POST', '/api/session', {
        title: title,
        agent: AGENT,
        model: MODEL,
        location: { directory: VAULT_DIR },
      });
      const sid = created.data.id;

      setStatus('⏳ Ингест в вики…', '#ffd666');
      await ocRequest('POST', '/api/session/' + sid + '/prompt', {
        text: buildPrompt(theme.id, md),
      });

      setStatus('✓ Готово, сессия открыта в новой вкладке', '#7fd67f');
      GM_openInTab(OC + WEB_PREFIX + '/session/' + sid, { active: true });
      setTimeout(() => resetBtn(btn), 5000);
    } catch (err) {
      console.error('[saby-ingest]', err);
      setStatus('✗ Ошибка: ' + err.message, '#ff8080');
      setTimeout(() => resetBtn(btn), 6000);
    }
  }

  function resetBtn(btn) {
    btn.title = 'Выкачать диалог в markdown и запустить ингест в вики (opencode)';
    const icon = btn.querySelector('.controls-icon');
    if (icon) icon.style.color = '';
  }

  function guessTitle(panel, themeId) {
    const raw = (panel.querySelector('.msg-ThemeView__header-info') || {}).innerText || '';
    const t = raw.replace(/\s+/g, ' ').trim();
    if (t) return t.slice(0, 80);
    return 'SBIS диалог ' + themeId.slice(0, 8);
  }

  let versionCache = null;
  function getVersion() {
    if (versionCache) return versionCache;
    const res = performance.getEntriesByType('resource').map(e => e.name);
    const hit = res.find(n => n.indexOf('x_version=') !== -1);
    if (hit) {
      versionCache = hit.split('x_version=')[1].split('&')[0];
      return versionCache;
    }
    return '';
  }

  async function getMarkdown(themeId) {
    const method = 'Сообщение.GetMarkdownText';
    const resp = await fetch('/msg/service/?x_version=' + getVersion(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'x-originalmethodname': btoa(unescape(encodeURIComponent(method))),
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        protocol: 7,
        method: method,
        params: { theme_id: themeId, message_count: 0 },
        id: 1,
      }),
    });
    if (!resp.ok) throw new Error('GetMarkdownText HTTP ' + resp.status);
    const data = await resp.json();
    if (!data.result) throw new Error('GetMarkdownText: пустой результат');
    return data.result;
  }

  function ocRequest(method, path, body) {
    return new Promise((resolve, reject) => {
      GM_xmlhttpRequest({
        method: method,
        url: OC + path,
        headers: {
          'Authorization': AUTH,
          'Content-Type': 'application/json',
        },
        data: body === undefined ? undefined : JSON.stringify(body),
        onload: r => {
          if (r.status >= 200 && r.status < 300) {
            try { resolve(JSON.parse(r.responseText)); } catch (e) { resolve({}); }
          } else {
            reject(new Error('opencode ' + path + ' -> HTTP ' + r.status + ': ' + r.responseText.slice(0, 300)));
          }
        },
        onerror: e => reject(new Error('opencode ' + path + ' -> сеть недоступна (opencode serve запущен?)')),
      });
    });
  }

  function buildPrompt(themeId, md) {
    return [
      'Проингестируй в вики этот диалог SBIS согласно скиллу wiki-ingest.',
      '',
      'Источник: диалог SBIS dev.saby.ru, theme_id: ' + themeId + ', выкачан: ' + new Date().toLocaleString('ru-RU'),
      '',
      'ХРАНИЛИЩЕ ВИКИ (явное указание пользователя): C:\\Users\\aa.timoshenko\\PycharmProjects\\claude-obsidian',
      'Этот репозиторий одновременно является рабочим хранилищем вики (внутри: inbox/, .raw/, wiki/ со страницами,',
      'hot.md, index.md, log.md). Правило «не использовать корень продукта как хранилище» здесь не применяется —',
      'пользователь явно выбирает этот путь. Работай с ним как с vault\'ом: источники — в inbox/ и .raw/, страницы — в wiki/.',
      '',
      'Текст диалога ниже (markdown):',
      '',
      '<dialog>',
      md,
      '</dialog>',
    ].join('\n');
  }
})();
