from src.core.interfaces.vacancy_notifier import IVacancyNotifier
from src.core.types.vacancy import Vacancy
from src.utils.chunk_iterator import iterate_by_chunks
from src.utils.telegram import escape_markdown_v2
from src.utils.telegram_sender import TelegramSender


class TelegramNotifier(IVacancyNotifier):
    VACANCIES_PER_MESSAGE = 15

    def __init__(self, telegram_sender: TelegramSender) -> None:
        self._sender = telegram_sender

    async def notify(self, vacancies: list[Vacancy]) -> None:
        vacancy_strings = [self.vacancy_view_str(v) for v in vacancies]

        await self._sender.send_message("**‼️ Новые вакансии**:")

        for v_strs in iterate_by_chunks(vacancy_strings, self.VACANCIES_PER_MESSAGE):
            await self._sender.send_message("\n".join(v_strs))

    @staticmethod
    def vacancy_view_str(vacancy: Vacancy) -> str:
        return f"""📭 [{escape_markdown_v2(vacancy.name)}]({escape_markdown_v2(vacancy.source_url)})
🛠️ **ID**: `{escape_markdown_v2(vacancy.id)}`"""
