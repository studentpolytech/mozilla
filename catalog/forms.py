from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text='Enter a date between now and 4 weeks (default 3).'
    )

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Проверка: дата не в прошлом
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date — date is in the past'))

        # Проверка: дата не дальше, чем на 4 недели вперёд
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date — more than 4 weeks ahead'))

        # Возвращаем очищенные данные
        return data
