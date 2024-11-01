import requests
from bs4 import BeautifulSoup


class AnitakuScrapper:
    def __init__(self):
        self.email = 'xetih74337@ofionk.com'
        self.password = 's\':yw5"E}5_y%bZ'
        self.login_url = 'https://anitaku.pe/login.html'
        self.session = requests.Session()

    def get_csrf_token(self):
        login_page = self.session.get(self.login_url)
        soup = BeautifulSoup(login_page.content, 'html.parser')

        token = soup.find('input', {'name': '_csrf'})
        return token['value']

    def login_to_website(self):
        login_data = {
            '_csrf': self.get_csrf_token(),
            'email': self.email,
            'password': self.password
        }

        response = self.session.post(self.login_url, data=login_data)
        return response.status_code

    def get_total_episodes(self, anime_url):
        response = self.session.get(anime_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # get ul with id 'episode_page'
        episode_page = soup.find('ul', {'id': 'episode_page'})

        # get last li tag
        last_page = episode_page.find_all('li')[-1]

        # get the 'a' tag from the last li tag
        last_page_link = last_page.find('a')

        # get 'ep_end' attribute from the 'a' tag
        total_episodes = int(last_page_link['ep_end'])

        return total_episodes

    def construct_episode_link(self, episode_number, anime_url):
        # replace episode-1 with episode-{episode_number}
        return anime_url.replace('episode-1', f'episode-{episode_number}')

    def get_episode_download_link(self, episode_link):
        response = self.session.get(episode_link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # get the div with class 'cf-download'
        download_div = soup.find('div', {'class': 'cf-download'})
        # get all 'a' tags from the div
        download_links = self._format_download_links(download_div.find_all('a'))

        return self.valid_download_link(download_links)

    def _format_download_links(self, download_links):
        links = {}
        for link in download_links:
            links[link.text.split('x')[1].strip()] = link['href']
        return links

    def valid_download_link(self, download_links):
        quality = ['360', '480', '720', '1080'][::-1]
        # check 1080 is available if true then return link
        for q in quality:
            if q in download_links and self._validate_download_link(download_links[q]):
                return download_links[q]
        return False

    def _validate_download_link(self, download_link):
        response = self.session.get(download_link, stream=True)
        # content length should be greater than 0
        return int(response.headers.get('content-length', 0)) > 0 and response.status_code == 200


# single instance of the scrapper
scrapper = AnitakuScrapper()
scrapper.login_to_website()

# download_link = scrapper.construct_episode_link(1, 'https://anitaku.pe/high-school-dxd-dub-episode-1')
# print(download_link)
# print(scrapper.get_episode_download_link(download_link))
