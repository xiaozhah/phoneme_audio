import os
import ui
import sound


# Define the button click event handler functions
def phoneme_tapped(sender):
    sound.stop_all_effects()  # Stop all currently playing sound effects
    sound_name = os.path.join("audio", sender.name + "_isolation.mp3")
    sound.play_effect(sound_name)


def word_tapped(sender):
    sound.stop_all_effects()  # Stop all currently playing sound effects
    sound_name = os.path.join("audio", sender.name + "_words.mp3")
    sound.play_effect(sound_name)


# Create the main view
scroll_view = ui.ScrollView()
scroll_view.background_color = "white"
scroll_view.flex = "WH"
scroll_view.content_size = (
    ui.get_screen_size().width,
    900,
)  # Assuming content height is 900, adjust as needed
content_view = ui.View(
    frame=(0, 0, scroll_view.content_size[0], scroll_view.content_size[1])
)
scroll_view.add_subview(content_view)

# Add the title label
title_label = ui.Label(frame=(0, 0, content_view.width, 40))
title_label.text = "Sounds"
title_label.font = ("<system-bold>", 24)
title_label.alignment = ui.ALIGN_CENTER
content_view.add_subview(title_label)

subtitle_label = ui.Label(frame=(0, 40, content_view.width, 30))
subtitle_label.text = "British English"
subtitle_label.font = ("<system>", 18)
subtitle_label.alignment = ui.ALIGN_CENTER
content_view.add_subview(subtitle_label)

instruction_label = ui.Label(frame=(0, 70, content_view.width, 30))
instruction_label.text = "Choose a sound to practise"
instruction_label.font = ("<system>", 16)
instruction_label.alignment = ui.ALIGN_CENTER
content_view.add_subview(instruction_label)

# Define the button content
sections = [
    (
        "Consonants",
        [
            ("p", "pen"),
            ("b", "bag"),
            ("t", "tie"),
            ("d", "dog"),
            ("k", "key"),
            ("g", "girl"),
            ("m", "man"),
            ("n", "nose"),
            ("ŋ", "singer"),
            ("f", "fall"),
            ("v", "van"),
            ("θ", "thin"),
            ("ð", "this"),
            ("s", "see"),
            ("z", "zoo"),
            ("ʃ", "shoe"),
            ("ʒ", "genre"),
            ("tʃ", "chain"),
            ("dʒ", "jazz"),
            ("l", "leg"),
            ("r", "red"),
            ("h", "house"),
            ("x", "Hanukkah"),
            ("j", "yes"),
            ("w", "wet"),
        ],
    ),
    (
        "Vowels",
        [
            ("iː", "eat"),
            ("i", "anyway"),
            ("ɪ", "if"),
            ("e", "egg"),
            ("æ", "add"),
            ("ə", "about"),
            ("ɜː", "earth"),
            ("ʌ", "up"),
            ("uː", "ooze"),
            ("u", "actual"),
            ("ʊ", "oops"),
            ("ɔː", "order"),
            ("ɒ", "on"),
            ("ɑː", "arm"),
        ],
    ),
    (
        "Diphthongs",
        [
            ("eɪ", "eight"),
            ("əʊ", "open"),
            ("aɪ", "ice"),
            ("aʊ", "out"),
            ("ɔɪ", "oil"),
            ("ɪə", "ear"),
            ("eə", "airport"),
            ("ʊə", "tourist"),
        ],
    ),
]

# Add the buttons
y_offset = 110
for section_title, buttons in sections:
    section_label = ui.Label(frame=(0, y_offset, content_view.width, 30))
    section_label.text = section_title
    section_label.font = ("<system-bold>", 20)
    section_label.alignment = ui.ALIGN_CENTER
    content_view.add_subview(section_label)
    y_offset += 40

    for i, (symbol, word) in enumerate(buttons):
        # Create a container view for the phoneme and word buttons
        container_view = ui.View(
            frame=(10 + (i % 6) * 60, y_offset + (i // 6) * 60, 50, 50)
        )
        container_view.border_width = 1
        container_view.corner_radius = 10

        # Create the phoneme button
        phoneme_button = ui.Button(name=symbol)
        phoneme_button.frame = (0, 0, container_view.width, container_view.height / 2)
        phoneme_button.background_color = "white"
        phoneme_button.tint_color = "black"
        phoneme_button.border_color = "white"
        phoneme_button.border_width = 1
        phoneme_button.corner_radius = 5
        phoneme_button.title = symbol
        phoneme_button.font = ("<system-bold>", 16)  # 设置音标按钮的字体为粗体
        phoneme_button.action = (
            phoneme_tapped  # Bind the phoneme event handler function
        )
        container_view.add_subview(phoneme_button)

        # Create the word button
        word_button = ui.Button(name=symbol)
        word_button.frame = (
            0,
            container_view.height / 2,
            container_view.width,
            container_view.height / 2,
        )
        word_button.background_color = "white"
        word_button.tint_color = "black"
        word_button.border_color = "white"
        word_button.border_width = 1
        word_button.corner_radius = 5
        word_button.title = word
        word_button.action = word_tapped  # Bind the word event handler function
        container_view.add_subview(word_button)

        content_view.add_subview(container_view)

    y_offset += (len(buttons) // 6 + 1) * 60

# Show the view
scroll_view.present("fullscreen")
