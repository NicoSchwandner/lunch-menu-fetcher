def build_menu_blocks(menu_data_list):
    blocks = []

    for menu_data in menu_data_list:
        # Add a header block for the restaurant name
        blocks.append(get_block_header(menu_data))

        # Add sections for each menu section
        for section in menu_data['sections']:
            # Add a section block with the heading
            blocks.append(get_block_section_header(section))

            # Add a section block with the items as bullet points
            items_text = "\n".join([f"• {item}" for item in section['items']])

            blocks.append(get_block_section_text(items_text))

            # Add a divider between sections
            blocks.append({
                "type": "divider"
            })

    return blocks

def get_block_header(menu_data):
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": menu_data['restaurant_name'],
            "emoji": True
        }
    }

def get_block_section_header(section):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*{section['heading']}*"
        }
    }

def get_block_section_text(items_text):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": items_text
        }
    }