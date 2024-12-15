import logging

def build_menu_blocks(logger: logging.Logger, menu_data):
    blocks = []

    # Add a header block for the restaurant name
    blocks.append(get_header(menu_data['restaurant_name']))

    restaurant_elements = []

    # Add sections for each menu section
    sections = menu_data['sections']
    for section in sections:
        # Add a section block with the heading
        restaurant_elements.append(get_rich_text_section_item_bold(section['heading']))

        section_items = []

        for item in section['items']:
            section_items.append(get_rich_text_section_item(item))

        restaurant_elements.append(get_rich_text_bullet_list(section_items))

    blocks.append(get_rich_text_node(restaurant_elements))

    return blocks

def get_header(text):
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True
        }
    }

def get_rich_text_node(children):
    return {
        "type": "rich_text",
        "elements": children
    }

def get_rich_text_section_node(children):
    return {
        "type": "rich_text_section",
        "elements": children
    }

def get_rich_text_bullet_list(children):
    return {
        "type": "rich_text_list",
        "style": "bullet",
        "elements": children
    }

def get_rich_text_section_item_bold(text):
    return {
        "type": "rich_text_section",
        "elements": [
            {
                "type": "text",
                "text": text,
                "style": {
                    "bold": True
                }
            }
        ]
    }

def get_rich_text_section_item(text):
    return {
        "type": "rich_text_section",
        "elements": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
