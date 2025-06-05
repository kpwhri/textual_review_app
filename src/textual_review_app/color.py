from rich.style import Style
from rich.text import Text

COLOR_NAMES = [
    'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'cyan',
    'magenta', 'black', 'white', 'gray', 'brown', 'pink',
    'lime', 'navy', 'olive', 'maroon', 'aqua', 'silver',
    'gold', 'indigo', 'violet', 'coral', 'salmon', 'sky',
]

COLOR_TO_BG_COLOR = {
    'red': 'red',
    'green': 'green',
    'blue': 'blue',
    'yellow': 'yellow',
    'orange': 'orange3',
    'purple': 'purple',
    'cyan': 'cyan',
    'magenta': 'magenta',
    'black': 'black',
    'white': 'white',
    'gray': 'gray50',
    'brown': 'rosy_brown',
    'pink': 'pink3',
    'lime': 'sea_green2',
    'navy': 'navy_blue',
    'olive': 'dark_olive_green1',
    'maroon': '#800000',
    'aqua': '#00FFFF',
    'silver': '#C0C0C0',
    'gold': '#EFBF04',
    'indigo': '#4B0082',
    'violet': 'violet',
    'coral': '#FF7F50',
    'salmon': '#FA8072',
    'sky': '#87CEEB',

}

COLOR_TO_TEXT_COLOR = {
    'red': 'black',
    'green': 'black',
    'blue': 'black',
    'yellow': 'black',
    'orange': 'black',
    'purple': 'black',
    'cyan': 'black',
    'magenta': 'black',
    'black': 'white',
    'white': 'black',
    'gray': 'black',
    'brown': 'black',
    'pink': 'black',
    'lime': 'black',
    'navy': 'white',
    'olive': 'black',
    'maroon': 'white',
    'aqua': 'black',
    'silver': 'black',
    'gold': 'black',
    'indigo': 'black',
    'violet': 'black',
    'coral': 'black',
    'salmon': 'black',
    'sky': 'black',
}


def test_colors():
    from rich import print as rprint
    for color in COLOR_NAMES:
        rprint(Text(f'* {color}',
                    style=Style(bgcolor=f'{COLOR_TO_BG_COLOR[color]}',
                                color=f'{COLOR_TO_TEXT_COLOR[color]}',
                                bold=True)))


if __name__ == '__main__':
    test_colors()
