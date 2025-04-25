import json
import requests
import openai
from pathlib import Path
from django.conf import settings
from gtts import gTTS
import wikipediaapi
from pydantic import BaseModel


class AuthorInfo(BaseModel):
    author_info: str
    author_works: str


wiki_wiki = wikipediaapi.Wikipedia(
    language='ko',
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
)


def get_wikipedia_image(book_author):
    URL = "https://ko.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": book_author,
        "prop": "pageimages",
        "format": "json",
        "piprop": "original",
    }
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for _, page_data in pages.items():
            original = page_data.get("original", {})
            if original:
                return original.get("source")
    return None


def get_wikipedia_content(book_author):
    page = wiki_wiki.page(book_author)
    if not page.exists():
        return None
    return {
        "summary": page.summary,
        "url": page.fullurl,
    }


def process_wikipedia_info(book):
    wiki_data = get_wikipedia_content(book.author)
    if wiki_data:
        wiki_summary = wiki_data.get("summary", "")
        img_url = get_wikipedia_image(book.author)
        if not book.pk:
            book.save()
        if img_url:
            response_img = requests.get(img_url)
            print(response_img)
            output_dir = Path(settings.MEDIA_ROOT) / "author_profiles"
            output_dir.mkdir(parents=True, exist_ok=True)
            original_filename = Path(img_url).name
            file_name = f"author_{book.pk}_{original_filename}"
            file_path = output_dir / file_name
            file_path.write_bytes(response_img.content)
            book.author_profile_img = str(Path("author_profiles") / file_name)
            book.save()
    else:
        wiki_summary = "위키피디아에서 정보를 찾을 수 없습니다."
    return wiki_summary


def generate_author_gpt_info(book, wiki_summary):
    prompt = f"""
        <도서 정보>
            책 제목: {book.title}
            작가: {book.author}
            위키피디아 요약: {wiki_summary}
        </도서 정보>
        """
    try:
        client = openai.OpenAI()
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    ################### 프롬프트 작성하기 ###################
                    "content": """ 프롬프트 작성하기
                                    답변 예시 : 
                                    {{ 
                                        "author_info": "작가 소개 예시입니다.",
                                        "author_works": "작품1, 작품2, 작품3"
                                    }}
                            .""",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=AuthorInfo,
            max_tokens=2040,
            temperature=0.5,
        )

        json_response = response.choices[0].message.content
        print(json_response)
        data = json.loads(json_response)
        author_info = data.get(
            "author_info", "작가 정보를 가져오지 못했습니다."
        )
        author_works = data.get(
            "author_works", "작품 목록을 가져오지 못했습니다."
        )
    except Exception as e:
        print("GPT 작가 정보 생성 에러:", e)
        author_info = "작가 정보를 가져오지 못했습니다."
        author_works = "작품 목록을 가져오지 못했습니다."
    return author_info, author_works


def generate_audio_script(book, wiki_summary):
    prompt_script = f"""
    - 책 제목: {book.title}
    - 작가: {book.author}
    - 책 설명: {book.description}
    - 작가 정보: {book.author_info}
    - 작가 대표작: {book.author_works}
    - 위키피디아 요약: {wiki_summary}
    """
    try:
        client = openai.OpenAI()
        response_script = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    ################### 프롬프트 작성하기 ###################
                    "content": "프롬프트 작성하기",
                },
                {"role": "user", "content": prompt_script},
            ],
            max_tokens=2040,
            temperature=0.7,
        )
        audio_script = response_script.choices[0].message.content.strip()
    except Exception as e:
        print("GPT Script 생성 에러:", e)
        audio_script = (
            "책과 작가 정보를 기반으로 한 소개 스크립트를 가져오지 못했습니다."
        )
    return audio_script


def create_tts_audio(book, audio_script):
    try:
        tts = gTTS(text=audio_script, lang='ko')
        file_name = f"tts_{book.pk}.mp3"
        output_dir = Path(settings.MEDIA_ROOT) / "tts"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name
        tts.save(str(output_path))
        return str(Path("tts") / file_name)
    except Exception as e:
        print("gTTS 음성 파일 생성 에러:", e)
        return None
