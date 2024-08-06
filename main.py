from enum import Enum
from typing import Dict, Any

import fire
import requests
from attr import define
from bs4 import BeautifulSoup
from cattrs import unstructure
from huggingface_hub import login
from rich.console import Console
from transformers import pipeline


@define
class Company:
    name: str
    link: str


class Role(Enum):
    SYSTEM = 'system'
    USER = 'user'


@define
class Message:
    role: Role
    content: str


@define
class Chat:
    messages: [Message] = []

    def as_system(self, prompt: str):
        self.messages.append(Message(Role.SYSTEM, prompt))

    def as_user(self, prompt):
        self.messages.append(Message(Role.USER, prompt))


@define
class DialogBilder:
    chat:Chat = Chat()

    @classmethod
    def act_as(cls, prompt: str):
        return DialogBilder().system(prompt)

    def system(self, prompt: str):
        self.chat.as_system(prompt)
        return self

    def user(self, prompt: str):
        self.chat.as_user(prompt)
        return self

    def build(self) -> Dict[str, Any]:
        return unstructure(self.chat.messages)


class RichConsole:
    def __init__(self):
        self._c = Console()

    def print(self, message: Any):
        self._c.print(message)


class CompaniesScanner(RichConsole):
    def __init__(self, companies: list[Company]):
        super().__init__()
        self._companies = companies
        self._system = DialogBilder.act_as(
            'Job finder. Your task is to check if the website contains any job offerings.')

    def jobs(self):
        self.print(f'Scanning {self._companies} for jobs (using: {self._system})')
        for c in self._companies:
            self.print(f'processing {c}')
            website_code = requests.get(c.link).text
            chat = self._system.user(f'the website code: {website_code}').build()
            pipe = pipeline("text-generation", "meta-llama/Meta-Llama-3-8B",
                            device_map="auto")
            response = pipe(chat, max_new_tokens=512)
            self.print(response)


class AiApplicationsApp(RichConsole):

    def scan(self, url):
        self.print(f'Scanning [bold yellow]{url}[/bold yellow]')
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        li_elements = soup.find_all("li", class_="articles-list__item")
        companies: [Company] = []
        for li in li_elements:
            company_name = li.find("h2", class_="article-preview__title").text.strip()
            company_link = li.find("a", class_="article-preview -external")["href"]
            companies.append(Company(company_name, company_link))

        for company in companies:
            self.print(company)

    def company(self, name: str, link: str):
        return CompaniesScanner([Company(name, link)])

    def login(self):
        login()


if __name__ == '__main__':
    fire.Fire(AiApplicationsApp)
