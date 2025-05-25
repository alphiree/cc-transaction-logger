from utils.extractors.base import BaseEmailExtractor


class MetrobankEmailExtractor(BaseEmailExtractor):
    def __init__(
        self,
        start_str: str = "at",
        end_str: str = "for PHP",
        str_to_find: str = "ending in ",
        merchant_email: str = "Customerservice@metrobankcard.com",
    ) -> None:
        super().__init__(merchant_email)
        self.start_str = start_str
        self.end_str = end_str
        self.str_to_find = str_to_find

    def extract_payment_info(
        self, text: str, subject: str | None = None
    ) -> tuple[str | None, float | None, str | None]:
        if subject == "Transaction Notification":
            start_index = text.find(self.str_to_find) + len(self.str_to_find)
            if start_index != -1:
                last_four_digits = text[start_index : start_index + 4]

            # Find indexes of start and end
            start_index = text.find(self.start_str) + len(self.start_str)
            end_index = text.find(self.end_str)
            if start_index != -1 and end_index != -1:
                merchant = text[start_index:end_index].strip()

            self.str_to_find = self.end_str
            start_index = text.find(self.str_to_find) + len(self.str_to_find)
            if start_index != -1:
                total_paid_amount = (
                    float(
                        "".join(
                            filter(
                                lambda x: x.isdigit(),
                                text[start_index : start_index + 10],
                            )
                        )
                    )
                    / 100
                )
            return last_four_digits, total_paid_amount, merchant
        else:
            return 0, 0, 0
