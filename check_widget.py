with open('chatbot/templates/chatbot/chat_widget.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = {
    'input->textarea':  '<textarea x-model' in html,
    'Enter to send':    '@keydown.enter.prevent' in html,
    'Auto-expand':      '@input' in html,
    'Markdown JS':      'marked.min.js' in html,
    'parseMarkdown fn': 'parseMarkdown' in html,
    'Markdown CSS':     '.markdown-body p' in html,
    'Suggestion pills': 'Show my pending tasks' in html,
    'user-select fix':  'user-select:none' in html,
    'line-clamp fix':   'line-clamp:2' in html and '-webkit-line-clamp:2' in html,
    'USER_INITIAL':     'window.USER_INITIAL' in html,
    'Django endif OK':  html.count('{% endif %}') >= 2,
}
for k, v in checks.items():
    status = 'OK' if v else 'MISSING'
    print(f'  {status}: {k}')
