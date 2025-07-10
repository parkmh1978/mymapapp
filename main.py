import streamlit as st
import folium
from streamlit_folium import st_folium

# 앱 제목
st.title("🇯🇵 도쿄 관광 명소 추천 지도")
st.markdown("한국인 관광객에게 인기 있는 도쿄 명소와 근처 맛집을 소개합니다! 🍜🍣")

# 지도 중심 좌표 (도쿄 중심)
tokyo_center = [35.6804, 139.7690]
m = folium.Map(location=tokyo_center, zoom_start=12)

# 관광 명소 및 맛집 데이터
places = [
    {
        "name": "1. 도쿄 캐릭터 스트리트",
        "location": [35.681167, 139.767052],
        "desc": "도쿄역 지하에 위치한 캐릭터 전문 상점 거리! 애니메이션 굿즈 쇼핑 천국 🎎",
        "food": {
            "name": "카레야 무텐카",
            "location": [35.680712, 139.766475],
            "desc": "순한 맛부터 매운 맛까지 다양한 일본식 카레 🍛"
        }
    },
    {
        "name": "2. 해리포터 스튜디오 도쿄",
        "location": [35.7364, 139.7130],
        "desc": "마법 세계로 떠나는 특별한 체험 공간! 🧙‍♂️🪄",
        "food": {
            "name": "버터비어 카페",
            "location": [35.7366, 139.7125],
            "desc": "해리포터 팬이라면 꼭! 버터비어 맛보기 🍺 (무알콜)"
        }
    },
    {
        "name": "3. 커비 카페 도쿄",
        "location": [35.6759, 139.7595],
        "desc": "귀여움 폭발! 커비 테마 카페 🎂",
        "food": {
            "name": "커비 디저트 바",
            "location": [35.6758, 139.7597],
            "desc": "딸기 팬케이크, 커비 모양 푸딩 등 인생샷 명소 📸"
        }
    }
]

# 지도에 마커 추가
for place in places:
    # 관광지 마커
    folium.Marker(
        location=place["location"],
        popup=f"<b>{place['name']}</b><br>{place['desc']}",
        tooltip=place["name"],
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

    # 맛집 마커
    food = place["food"]
    folium.Marker(
        location=food["location"],
        popup=f"<b>{food['name']}</b><br>{food['desc']}",
        tooltip=food["name"],
        icon=folium.Icon(color='red', icon='cutlery')
    ).add_to(m)

# Streamlit에 지도 표시
st_data = st_folium(m, width=700, height=500)
