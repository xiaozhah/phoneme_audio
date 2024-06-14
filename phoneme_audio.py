import os
import ui
import sound

# Define the button click event handler function
def button_tapped(sender):
    sound_name = os.path.join('audio', sender.name + '_isolation.mp3')
    sound.play_effect(sound_name)

# Create the main view
scroll_view = ui.ScrollView()
scroll_view.background_color = 'white'
scroll_view.flex = 'WH'
scroll_view.content_size = (ui.get_screen_size().width, 900)  # Assuming content height is 1500, adjust as needed
content_view = ui.View(frame=(0, 0, scroll_view.content_size[0], scroll_view.content_size[1]))
scroll_view.add_subview(content_view)

# Add the title label
title_label = ui.Label(frame=(0, 0, content_view.width, 40))
title_label.text = "Sounds"
title_label.font = ('<system-bold>', 24)
title_label.alignment = ui.ALIGN_CENTER
content_view.add_subview(title_label)

subtitle_label = ui.Label(frame=(0, 40, content_view.width, 30))
subtitle_label.text = "British English"
subtitle_label.font = ('<system>', 18)
subtitle_label.alignment = ui.ALIGN_CENTER
content_view.add_subview(subtitle_label)

instruction_label = ui.Label(frame=(0, 70, content_view.width, 30))
instruction_label.text = "Choose a sound to practise"
instruction_label.font = ('<system>', 16)
instruction_label.alignment = ui.ALIGN_CENTER
content_view.add_subview(instruction_label)

# Define the button content
sections = [
    ("Consonants", [
        ("p", "pen"), ("b", "bad"), ("t", "tea"), ("d", "did"), ("k", "cat"), ("g", "get"),
        ("m", "man"), ("n", "now"), ("ŋ", "sing"), ("f", "fall"), ("v", "van"),
        ("θ", "thin"), ("ð", "this"), ("s", "see"), ("z", "zoo"), ("ʃ", "shoe"), ("ʒ", "vision"),
        ("tʃ", "chain"), ("dʒ", "jam"), ("l", "leg"), ("r", "red"), ("h", "hat"), ("x", "loch"),
        ("j", "yes"), ("w", "wet")
    ]),
    ("Vowels", [
        ("iː", "see"), ("ɪ", "happy"), ("e", "bed"), ("æ", "cat"),
        ("ə", "about"), ("ɜː", "fur"), ("ʌ", "cup"), ("uː", "too"), ("ʊ", "put"),
        ("ɔː", "saw"), ("ɒ", "got"), ("ɑː", "father")
    ]),
    ("Diphthongs", [
        ("eɪ", "say"), ("əʊ", "go"), ("aɪ", "my"), ("aʊ", "now"), ("ɔɪ", "boy"),
        ("ɪə", "near"), ("eə", "hair"), ("ʊə", "pure")
    ])
]

# Add the buttons
y_offset = 110
for section_title, buttons in sections:
    section_label = ui.Label(frame=(0, y_offset, content_view.width, 30))
    section_label.text = section_title
    section_label.font = ('<system-bold>', 20)
    section_label.alignment = ui.ALIGN_CENTER
    content_view.add_subview(section_label)
    y_offset += 40
    
    for i, (symbol, word) in enumerate(buttons):
        # Create the button
        button = ui.Button(name=symbol)
        button.frame = (10 + (i % 6) * 60, y_offset + (i // 6) * 60, 50, 50)
        button.background_color = 'white'
        button.tint_color = 'black'
        button.border_width = 1
        button.corner_radius = 5
        button.action = button_tapped  # Bind the event handler function
        
        # Create the label to display multi-line text
        label = ui.Label()
        label.frame = (0, 0, button.width, button.height)
        label.text = f"{symbol}\n{word}"
        label.font = ('<system>', 16)
        label.alignment = ui.ALIGN_CENTER
        label.number_of_lines = 2  # Allow multiple lines
        button.add_subview(label)
        
        content_view.add_subview(button)
    
    y_offset += (len(buttons) // 6 + 1) * 60

# Show the view
scroll_view.present('fullscreen')
