from app.schemas import RecommendLocationResponse, RecommendLocationRequest
from fastapi import HTTPException
import boto3
import joblib
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

def get_recommendations(request: RecommendLocationRequest):
    try:
        #download_files()

        #model_sample, label_encoder_gungu = load_resources()

        #responses = make_survey_result(request)

        #recommend_region = predict_region(responses, model_sample, label_encoder_gungu)

        return RecommendLocationResponse(locationNames=["yangyang", "chuncheon", "sockcho"])
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


"""s3 파일 다운로드"""
def download_files():
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    download_folder = 'downloads'

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    files_to_download = [
        ('model/catboost_model_sample.pkl', 'catboost_model_sample.pkl'),
        ('model/label_encoder_gungu.pkl', 'label_encoder_gungu.pkl'),
        ('model/train_set.csv', 'train_set.csv')
    ]

    for s3_file, local_file in files_to_download:
        local_file_path = os.path.join(download_folder, local_file)

        if not os.path.exists(local_file_path):
            print(f"Downloading {s3_file} to {local_file_path}...")
            s3.download_file('dna-kangwon', s3_file, local_file_path)
        else:
            print(f"{local_file_path} already exists. Skipping download.")


"""설문 결과"""
def make_survey_result(request: RecommendLocationRequest):
    responses = {}

    # 여행시 가장 하고 싶은 활동
    responses['TRAVEL_MISSION_PRIORITY'] = request.activities

    # 최근 다녀온 여행에서 방문한 곳의 유형
    responses['VISIT_AREA_TYPE_CD'] = request.visitTypes

    # 본인의 수입
    responses['INCOME'] = request.incomeRanges

    # 잘 알려지지 않은 방문지와 잘 알려진 방문지 중 선호하는 유형
    responses['TRAVEL_STYL_6'] = request.preferenceTypes

    # 1년에 여행을 몇 번정도 하나요?
    responses['TRAVEL_NUM'] = request.tripCount

    # 편하지만 비싼 숙소와 불편하지만 저렴한 숙소 중 선호하는 유형
    responses['TRAVEL_STYL_4'] = request.accommodationPreference

    # 워케이션을 통해서 얻고자 하는 바는?
    responses['TRAVEL_MOTIVE_1'] = request.workationGoals

    # 휴양과 체험 중 선호하는 유형
    responses['TRAVEL_STYL_5'] = request.relaxationExperience

    # 사진 촬영 중요하지 않음 vs 사진촬영 중요함 중 선호하는 유형은?
    responses['TRAVEL_STYL_8'] = request.photoImportance

    return responses


"""모델과 레이블 인코더 로드"""
def load_resources():
    model_sample = joblib.load('downloads/catboost_model_sample.pkl')
    label_encoder_gungu = joblib.load('downloads/label_encoder_gungu.pkl')
    return model_sample, label_encoder_gungu


"""응답을 기반으로 지역 예측"""
def predict_region(responses, model_sample, label_encoder_gungu):
    cat_vars = ['GUNGU', 'VISIT_AREA_TYPE_CD', 'TRAVEL_MOTIVE_1', 'TRAVEL_MISSION_PRIORITY']

    # 응답을 데이터프레임으로 변환
    survey_df = pd.DataFrame([responses])

    # 더미 코드
    survey_df['GUNGU'] = '양양'

    Train = pd.read_csv('downloads/train_set.csv')
    X_train = Train[survey_df.columns]

    regions_str = "철원군, 화천군, 양구군, 고성군, 속초시, 양양군, 인제군, 춘천시, 홍천군, 강릉시, 평창군, 횡성군, 원주군, 영월군, 정선군, 동해시, 삼척시, 태백시"

    # 쉼표와 공백을 기준으로 문자열을 나누어 리스트로 변환
    kw_list = [region.strip() for region in regions_str.split(',')]

    intersection_list = list(set(X_train['GUNGU']).intersection(set(kw_list)))

    # 범주형 변수 처리
    for feature in cat_vars:
        survey_df[feature] = survey_df[feature].astype(str)

    X_train['GUNGU'] = label_encoder_gungu.transform(X_train['GUNGU'])

    unique_gungu_values = X_train['GUNGU'].unique()

    gungu = np.unique(label_encoder_gungu.inverse_transform(X_train['GUNGU'].astype(int)))
    results_df = pd.DataFrame(columns=gungu)

    for value in unique_gungu_values:
        reverse_value = label_encoder_gungu.inverse_transform(np.array(int(value)).reshape(-1, 1))

        # GUNGU 값을 바꾼 데이터프레임 생성
        X_temp = survey_df.copy()
        X_temp['GUNGU'] = value
        X_temp['GUNGU'] = X_temp['GUNGU'].astype(str)

        cols = list(X_temp.columns)
        cols.remove('GUNGU')
        cols = ['GUNGU'] + cols
        X_temp = X_temp[cols]

        predictions = model_sample.predict(X_temp)

        # 예측 결과를 데이터프레임에 추가
        results_df[reverse_value[0]] = predictions

    recommend_region = results_df[intersection_list].idxmax(axis=1)[0]
    return ["yangyang", "chuncheon", "sockcho"]
