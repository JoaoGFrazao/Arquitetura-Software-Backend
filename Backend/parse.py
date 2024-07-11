import xml.etree.ElementTree as ET

def parse_bgg_response(xml_data):
    root = ET.fromstring(xml_data)
    games = []
    for item in root.findall('item'):
        game = {
            'id': item.get('id'),
            'name': item.find('name').get('value'),
            'yearpublished': item.find('yearpublished').get('value') if item.find('yearpublished') is not None else 'N/A',
        }
        games.append(game)
    return games


def parse_bgg_add(xml_data):
    root = ET.fromstring(xml_data)
    item = root.find('item')
    if item is None:
        return None

    game = {
        'minplayers': item.find('minplayers').get('value') if item.find('minplayers') is not None else 'N/A',
        'maxplayers': item.find('maxplayers').get('value') if item.find('maxplayers') is not None else 'N/A',
        'minage': item.find('minage').get('value') if item.find('minage') is not None else 'N/A',
        'playingtime': item.find('playingtime').get('value') if item.find('playingtime') is not None else 'N/A',
        'name': item.find('name').get('value'),
        'yearpublished': item.find('yearpublished').get('value') if item.find('yearpublished') is not None else 'N/A',
    }
    return game