with open('chatbot/templates/chatbot/chat_widget.html', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if "{% if request.user.is_superuser or request.user.role == 'MANAGEMENT'" in line and not line.strip().endswith('%}'):
        # Merge next line into this one
        merged = line.rstrip('\r\n') + ' ' + lines[i+1].lstrip()
        new_lines.append(merged + '\n')
        i += 2  # Skip next line
    else:
        new_lines.append(line)
        i += 1

with open('chatbot/templates/chatbot/chat_widget.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Fixed!')
