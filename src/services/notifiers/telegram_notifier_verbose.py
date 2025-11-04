from json import dumps

from core.interfaces.vacancy_notifier import IVacancyNotifier
from core.types.vacancy import Vacancy
from utils.chunk_iterator import iterate_by_chunks
from utils.telegram import escape_markdown_v2
from utils.telegram_sender import TelegramSender


class TelegramNotifierVerbose(IVacancyNotifier):
    VACANCIES_PER_MESSAGE = 5

    def __init__(self, telegram_sender: TelegramSender) -> None:
        self._sender = telegram_sender

    async def notify(self, vacancies: list[Vacancy]) -> None:
        vacancy_strings = [self.vacancy_view_str(v) for v in vacancies]

        for v_strs in iterate_by_chunks(vacancy_strings, self.VACANCIES_PER_MESSAGE):
            await self._sender.send_message("\n\n".join(v_strs))

    @staticmethod
    def vacancy_view_str(vacancy: Vacancy) -> str:
        return f"""📭 [{escape_markdown_v2(vacancy.name)}]({escape_markdown_v2(vacancy.source_url)})
📝**Описание**: {escape_markdown_v2(vacancy.details[0:100])}
💡**Доп\\. информация**: ```
{escape_markdown_v2(dumps(vacancy.additional_data, indent=2, ensure_ascii=False))}
```
🛠️ **ID**: `{escape_markdown_v2(vacancy.id)}`
🛠️ **SOURCE\\_ID**: `{escape_markdown_v2(vacancy.source_id)}`
🛠️ **SCRAPER**: `{escape_markdown_v2(vacancy.scraper_name)}`"""
