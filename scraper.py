import csv
import requests
from lxml import html


# Target URL
url = 'https://nsusharks.com/roster.aspx?rp_id=5066'

# Request headers
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
accept = 'application/json, text/javascript, */*; q=0.01'
referer = ''

# List of all collected rows
soccer_player_data = []

# Empty row separator
csv_empty_row = []


# Collect all tables with data
def parse_section_tables(tree):
    result_data = []
    gamehigh_stats_sections = tree.xpath('//section')

    # Iterate over sections
    for section in gamehigh_stats_sections:
        # Section title
        section_title = section.xpath('./h5/text()')
        result_data.append(section_title)

        # Table headings
        table_headings = section.xpath('.//thead//th/text()')
        result_data.append(table_headings)

        # Table rows
        table_rows = section.xpath('.//tbody/tr')
        for row in table_rows:
            row_data = row.xpath('./td//text() | ./th/a/text()')
            result_data.append(row_data)

        # Table foot
        table_foot = section.xpath('.//tfoot//td | .//tfoot//th')
        if table_foot:
            foot = []
            for i in table_foot:
                cell = i.xpath('./text()')
                if cell:
                    foot.append(cell[0])
                else:
                    foot.append('')
            result_data.append(foot)

        result_data.append(csv_empty_row)

    return result_data


def main(url):
    # Request to soccer player page
    page = requests.get(url, headers={'User-Agent': user_agent})

    # Select elements with lxml
    tree = html.fromstring(page.content)

    # Soccer player name
    player_name_element = tree.xpath('//span[@class="sidearm-roster-player-name"]/span/text()')
    player_name = ' '.join(player_name_element)

    soccer_player_data.append([player_name.upper(), ])
    soccer_player_data.append(csv_empty_row)

    # name for .csv file
    csv_name = player_name.replace(' ', '_').lower()

    # Soccer player fields
    player_fields = tree.xpath('//div[contains(@class, "sidearm-roster-player-fields")]//li')
    soccer_player_data.append(tree.xpath('//div[contains(@class, "sidearm-roster-player-fields")]//li//dt//text()'))
    soccer_player_data.append(tree.xpath('//div[contains(@class, "sidearm-roster-player-fields")]//li//dd//text()'))
    soccer_player_data.append(csv_empty_row)

    # Fake ajax request to retrive the stats tables
    url = 'https://nsusharks.com/services/responsive-roster-bio.ashx?type=stats&rp_id=5066&path=msoc&year=2018&player_id=0'

    page = requests.get(url, headers={'User-Agent': user_agent, 'Accept': accept, 'Referer': referer})

    # Parse json response
    ajax_response = page.json()

    # Get gamehigh_stats tables data
    tree = html.fromstring(ajax_response['gamehigh_stats'])
    soccer_player_data.extend(parse_section_tables(tree))

    # Get current_stats tables data
    tree = html.fromstring(ajax_response['current_stats'])
    soccer_player_data.extend(parse_section_tables(tree))

    # Save all collected data rows to .csv file
    with open(csv_name + '.csv', 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(soccer_player_data)

if __name__ == '__main__':
    main(url)
