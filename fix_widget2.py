import re
import os

print('Current dir:', os.getcwd())
try:
    with open('chat_widget_git.html', 'r', encoding='utf-8') as f:
        html = f.read()
except UnicodeDecodeError:
    with open('chat_widget_git.html', 'r', encoding='utf-16') as f:
        html = f.read()

# Fix 1: Django tags
html = re.sub(r'{%\s*endif\s*%}\s*{%\s*endif\s*%}\s*$', '{% endif %}\n', html)
html = re.sub(r'{%\s*if\s*request\.user\.is_superuser\s*or\s*request\.user\.role\s*==\s*\'MANAGEMENT\'[^%]*%}', 
              "{% if request.user.is_superuser or request.user.role == 'MANAGEMENT' or request.user.role == 'MANAGER' %}", html, flags=re.DOTALL)

# Fix 2: Avatar bug
if 'window.USER_INITIAL =' not in html:
    html = html.replace('{{ request.user.username|first|upper }}', '''<script>
    window.USER_INITIAL = "{{ request.user.username|first|upper|default:'U'|escapejs }}";
</script>''', 1)

html = re.sub(r'<span[^>]*>{{[^}]+}}</span>', 
              '<span style="color:#fff;font-size:10px;font-weight:700;" x-text="window.USER_INITIAL"></span>', html)

# Fix 3: AlpineJS Flex bubbles issue
html = re.sub(r':style="\'display:flex; margin-bottom: 2px; justify-content:\' \+ \(msg\.role === \'user\' \? \'flex-end\' : \'flex-start\'\)"', 
              ':style="msg.role === \'user\' ? \'display:flex; margin-bottom: 2px; justify-content: flex-end\' : \'display:flex; margin-bottom: 2px; justify-content: flex-start\'"', html)
html = re.sub(r':style="\'max-width:85%; display:flex; flex-direction:column; align-items:\' \+ \(msg\.role === \'user\' \? \'flex-end\' : \'flex-start\'\)"', 
              ':style="msg.role === \'user\' ? \'max-width:85%; display:flex; flex-direction:column; align-items: flex-end\' : \'max-width:85%; display:flex; flex-direction:column; align-items: flex-start\'"', html)

# Fix 4: CSS warnings (user-select, line-clamp)
html = html.replace('select:none;', 'user-select:none;')
html = html.replace('-webkit-line-clamp:2;', '-webkit-line-clamp:2;line-clamp:2;')

# Fix 5: Auto-expanding textarea & Enter to send
replace_input = '''<input type="text" x-model="inputMessage" placeholder="Type a message…"
                                    :disabled="isLoading"
                                    style="flex:1;border:1.5px solid #e2e8f0;border-radius:12px;padding:9px 14px;font-size:13px;color:#1e293b;background:#f8fafc;outline:none;transition:border .2s;"
                                    onfocus="this.style.borderColor='#6366f1';this.style.background='#fff';"
                                    onblur="this.style.borderColor='#e2e8f0';this.style.background='#f8fafc';">'''
replace_textarea = '''<textarea x-model="inputMessage" placeholder="Type a message…"
                                    :disabled="isLoading"
                                    @keydown.enter.prevent="sendMessage()"
                                    @input="$event.target.style.height = 'auto'; $event.target.style.height = $event.target.scrollHeight + 'px';"
                                    style="flex:1;border:1.5px solid #e2e8f0;border-radius:12px;padding:10px 14px;font-size:13px;color:#1e293b;background:#f8fafc;outline:none;transition:border .2s;resize:none;min-height:40px;max-height:120px;overflow-y:auto;"
                                    onfocus="this.style.borderColor='#6366f1';this.style.background='#fff';"
                                    onblur="this.style.borderColor='#e2e8f0';this.style.background='#f8fafc';"></textarea>'''
html = html.replace(replace_input, replace_textarea)

# Fix 6: Suggestion Prompts
empty_state_old = '''            <!-- Empty state -->
            <div x-show="messages.length===0"
                style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;padding:24px;">
                <div
                    style="width:56px;height:56px;background:linear-gradient(135deg,#6366f1,#4338ca);border-radius:16px;display:flex;align-items:center;justify-content:center;margin-bottom:12px;box-shadow:0 8px 24px rgba(99,102,241,.35);">
                    <i class="fa-solid fa-robot" style="color:#fff;font-size:22px;"></i>
                </div>
                <p style="font-weight:700;font-size:14px;color:#1e293b;margin:0 0 6px;">How can I help you?</p>
                <p style="font-size:12px;color:#94a3b8;margin:0;line-height:1.6;max-width:220px;">Ask about tasks,
                    meetings, or projects. Press 📞 for voice call!</p>
            </div>'''
            
empty_state_new = '''            <!-- Empty state -->
            <div x-show="messages.length===0"
                style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;padding:24px;">
                <div
                    style="width:56px;height:56px;background:linear-gradient(135deg,#6366f1,#4338ca);border-radius:16px;display:flex;align-items:center;justify-content:center;margin-bottom:12px;box-shadow:0 8px 24px rgba(99,102,241,.35);">
                    <i class="fa-solid fa-robot" style="color:#fff;font-size:22px;"></i>
                </div>
                <p style="font-weight:700;font-size:14px;color:#1e293b;margin:0 0 6px;">How can I help you?</p>
                <p style="font-size:12px;color:#94a3b8;margin:0 0 16px;line-height:1.6;max-width:220px;">Ask about tasks,
                    meetings, or projects. Press 📞 for voice call!</p>
                
                <!-- Suggested Prompts -->
                <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;max-width:260px;">
                    <button @click="inputMessage='Show my pending tasks'; sendMessage()" style="background:#fff;border:1px solid #e2e8f0;padding:6px 12px;border-radius:14px;font-size:11px;color:#475569;cursor:pointer;transition:all .2s;" onmouseover="this.style.borderColor='#6366f1';this.style.color='#6366f1'" onmouseout="this.style.borderColor='#e2e8f0';this.style.color='#475569'">Show my pending tasks</button>
                    <button @click="inputMessage='Create a new meeting'; sendMessage()" style="background:#fff;border:1px solid #e2e8f0;padding:6px 12px;border-radius:14px;font-size:11px;color:#475569;cursor:pointer;transition:all .2s;" onmouseover="this.style.borderColor='#6366f1';this.style.color='#6366f1'" onmouseout="this.style.borderColor='#e2e8f0';this.style.color='#475569'">Create a new meeting</button>
                    <button @click="inputMessage='Any events today?'; sendMessage()" style="background:#fff;border:1px solid #e2e8f0;padding:6px 12px;border-radius:14px;font-size:11px;color:#475569;cursor:pointer;transition:all .2s;" onmouseover="this.style.borderColor='#6366f1';this.style.color='#6366f1'" onmouseout="this.style.borderColor='#e2e8f0';this.style.color='#475569'">Any events today?</button>
                </div>
            </div>'''
html = html.replace(empty_state_old, empty_state_new)

# Fix 7: Markdown Rendering Support
if 'marked.min.js' not in html:
    html = html.replace('<script defer src="https://cdn.jsdelivr.net', '<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>\n<script defer src="https://cdn.jsdelivr.net')
    
html = html.replace('''<p style="margin:0;white-space:pre-wrap;word-break:break-word;" x-text="msg.content"></p>''',
'''<div x-show="msg.role === 'assistant'" class="markdown-body" style="margin:0;word-break:break-word;font-size:14px;line-height:1.6;" x-html="parseMarkdown(msg.content)"></div>
                            <p x-show="msg.role === 'user'" style="margin:0;white-space:pre-wrap;word-break:break-word;" x-text="msg.content"></p>''')

html = html.replace('csrf() { const m = document.cookie.match(/csrftoken=([^;]+)/); return m ? m[1] : \'\'; }',
'''csrf() { const m = document.cookie.match(/csrftoken=([^;]+)/); return m ? m[1] : ''; },
            parseMarkdown(text) {
                if (!text) return '';
                try {
                    return typeof marked !== 'undefined' ? marked.parse(text) : text;
                } catch(e) { return text; }
            }''')

css_append = '''
    /* Markdown Styles */
    .markdown-body p { margin: 0 0 8px; }
    .markdown-body p:last-child { margin: 0; }
    .markdown-body strong { font-weight: 700; color: #1e293b; }
    .markdown-body ul, .markdown-body ol { margin: 4px 0 8px 16px; padding: 0; }
    .markdown-body li { margin-bottom: 4px; }
    .markdown-body pre { background: rgba(0,0,0,0.04); padding: 8px; border-radius: 6px; overflow-x: auto; font-size: 12px; margin: 8px 0; border: 1px solid rgba(0,0,0,0.05); }
    .markdown-body code { background: rgba(0,0,0,0.04); padding: 2px 4px; border-radius: 4px; font-family: monospace; font-size: 12px; }
    .markdown-body a { color: #6366f1; text-decoration: none; }
    .markdown-body a:hover { text-decoration: underline; }
</style>'''
html = html.replace('</style>', css_append)

with open('chatbot/templates/chatbot/chat_widget.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Rewrite completed safely using Python')
