from django import forms
from .models import Book, Thread


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = [
            "author_info",
            "author_profile_img",
            "author_works",
            "audio_file",
        ]

class ThreadForm(forms.ModelForm):
    # 다양한 날짜 형식을 지원하도록 수정
    reading_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],  # 여러 날짜 형식 허용
        widget=forms.DateInput(attrs={'type': 'date'})  # HTML5 날짜 선택기 사용
    )
    
    class Meta:
        model = Thread
        fields = ('title', 'content', 'reading_date', 'cover_img')  # cover_img 
