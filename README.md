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
- 0.1.0 (Sunday, 18 December 2016)
  - Github repository에서 가장 최근에 star가 증가한 repo 가져오기 (all language)
  - Naver IT news scrawling

- 0.2.0 (Monday, 26 December 2016)
  - Post twitter 기능 추가
  - Use naver openapi url 주소 짧게 줄이는 기능 추가 (트위터 140자 제한)
  - Coex 전시회 조회 기능 추가
  - Github 언어별 조회조건 추가
  - Stackoverflow vote가 증가한 게시판 정보 수집 기능 추가 (python)

- 0.3.0 (Monday, 1 January 2017)
  - Gmail 전송기능 추가
  - Daum 블로그 조회기능 추가
  - Nate ranking new 조회 추가

- 0.3.1 (Friday, 27 January 2017)
  - 중복된 조회정보 전송 방지 기능 추가 (SQlite3 DB에 전송한 url 정보 저장)
  - cgitb를 디버깅하기 위해 추가 
  - Stackoverflow에 racket 언어 추가
  - OpenAPI(data.go.kr) 조회 기능 추가
  - Naver 인기있는 뉴스 조회 추가
  - 국립중앙박물관(이촌) 전시 정보 조회 추가

- 0.3.2 (Thursday, 16 February 2017)
  - 트위터에 특정 키워드 조회 기능 추가
  - bug fix (예외 처리 추가)
  - OpenAPI로 공정률 조회 추가
  - HackerNews 31~60위 조회 추가
  - MBN 부동산 뉴스 조회 추가

- 0.4.0 (Friday, 24 February 2017)
  - setup.py 추가
  - 소스코드 모듈화

- 0.4.1 (current)
  - logging 추가, logger 사용
  - configure file path 변경 (./ -> ~/)
  - 140 초과 메시지 전송 기능 추가, 초과되는 문자열 삭제 후 포스팅

License
-------
Find_the_treasure is licensed under the terms of the MIT License (see the file LICENSE).
