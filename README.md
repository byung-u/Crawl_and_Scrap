find_the_treasure
----------------

웹 스크롤링, openAPI 호출을 이용하여 의미있는 정보를 수집해보기 위한 파이썬 유틸리티.
Oauth, 인증키가 너무 많이 필요한 번거로움이...

- 요약 가능한 정보는 url주소와 함께 트위터 전송
- 긴 정보는 개인 G메일 전송

Quick Start
----------------
- Requirements

  - Python 3.x
  - Twitter Oauth
  - Github Oauth
  - Naver Oauth
  - Daum Oauth
  - OpenAPI key (www.data.go.kr)
  - Gmail account

수집 정보
---------
- 트위터 전송
  - Github repository star 개수 갱신 체크해서 개수가 증가한 것
  - Stackoverflow upvote 갱신 체크 개수가 증가한 것
  - data.go.kr 관심있는 지역의 아파트 가격, 공정률 정보
  - 국립중앙박물관(이촌) 전시 정보 
  - Coex 전시 정보
  - MBN 부동산 news 

- 이메일 전송
  - nate ranking 뉴스
  - naver IT 뉴스
  - daum 부동산 뉴스

Release
-------
