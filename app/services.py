from app.schemas import RecommendLocationResponse, RecommendLocationRequest, Location
from fastapi import HTTPException
import boto3
import joblib
import pandas as pd
import os
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()
download_folder = 'downloads'

def get_recommendations(request: RecommendLocationRequest):
    try:
        download_files()

        model_sample, label_encoder_gungu = load_resources()

        survey_responses = make_survey_result(request)

        kw_recommend = predict_region(survey_responses, model_sample, label_encoder_gungu)

        return RecommendLocationResponse(locations=[Location(**item) for item in kw_recommend])
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


"""s3 파일 다운로드"""
def download_files():
    bucket = 'dna-kangwon'
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    files_to_download = [
        ('model/catboost_best_model_0.794.pkl', 'catboost_best_model_0.794.pkl'),
        ('model/label_encoder_gungu.pkl', 'label_encoder_gungu.pkl'),
        ('model/train_selected.csv', 'train_selected.csv'),
        ('model/워케이션 순위.csv', '워케이션 순위.csv')
    ]

    for s3_file, local_file in files_to_download:
        local_file_path = os.path.join(download_folder, local_file)

        if not os.path.exists(local_file_path):
            print(f"Downloading {s3_file} to {local_file_path}...")
            s3.download_file(bucket, s3_file, local_file_path)
        else:
            print(f"{local_file_path} already exists. Skipping download.")


"""모델과 레이블 인코더 로드"""
def load_resources():
    model_sample = joblib.load(download_folder + '/catboost_best_model_0.794.pkl')
    label_encoder_gungu = joblib.load(download_folder + '/label_encoder_gungu.pkl')
    return model_sample, label_encoder_gungu


"""설문 결과"""
def make_survey_result(request: RecommendLocationRequest):
    responses = {}

    # 1. 성별
    responses['GENDER'] = request.gender

    # 2. 나이
    age_input = request.age
    if age_input >= 60:
        responses['AGE_GRP'] = 60
    else:
        responses['AGE_GRP'] = (age_input // 10) * 10

    # 3. 소득
    responses['INCOME'] = request.income

    # 4. 워케이션 계획 인원
    responses['TRAVEL_COMPANIONS_NUM'] = request.travelCompanions

    # 5. 자연과 도시 선호
    responses['TRAVEL_STYL_1'] = request.travelPreference

    # 6. 새로운 지역과 익숙한 지역 선호
    responses['TRAVEL_STYL_3'] = request.newOrFamiliar

    # 7. 편하지만 비싼 여행 vs 불편하지만 저렴한 여행
    responses['TRAVEL_STYL_4'] = request.comfortVsCost

    # 8. 휴양/휴식 vs 체험 활동
    responses['TRAVEL_STYL_5'] = request.relaxationVsActivities

    # 9. 잘 알려지지 않은 방문지 vs 잘 알려진 방문지
    responses['TRAVEL_STYL_6'] = request.knownVsUnknown

    # 10. 사진 촬영 중요성
    responses['TRAVEL_STYL_8'] = request.photographyImportance

    return responses


"""응답을 기반으로 특정 지역의 만족도 예측"""
def predict_region(responses, model_sample, label_encoder_gungu):
    # 응답을 데이터프레임으로 변환
    survey_df = pd.DataFrame([responses])

    # 더미 코드
    survey_df['GUNGU'] = '양양'
    survey_df['CEI'] = 4.0

    Train = pd.read_csv(download_folder + '/train_selected.csv')

    survey_df = survey_df[Train.columns]
    survey_df[['AGE_GRP', 'INCOME', 'TRAVEL_COMPANIONS_NUM']] = survey_df[
        ['AGE_GRP', 'INCOME', 'TRAVEL_COMPANIONS_NUM']].astype(int)
    cols_to_object = survey_df.columns.difference(['AGE_GRP', 'INCOME', 'TRAVEL_COMPANIONS_NUM', 'CEI'])
    survey_df[cols_to_object] = survey_df[cols_to_object].astype(object)

    regions_str = "속초시, 횡성군, 정선군, 양양군, 홍천군, 인제군, 춘천시, 삼척시, 강릉시, 고성군, 평창군, 영월군"

    # 쉼표와 공백을 기준으로 문자열을 나누어 리스트로 변환
    kw_list = [region.strip() for region in regions_str.split(',')]

    unique_gungu_values = Train['GUNGU'].unique()

    results_df = pd.DataFrame(columns=unique_gungu_values)

    for region in unique_gungu_values:
        # GUNGU 값을 바꾼 데이터프레임 생성
        X_temp = survey_df.copy()
        X_temp['GUNGU'] = region

        predictions = model_sample.predict(X_temp)

        # 예측 결과를 데이터프레임에 추가
        results_df[region] = predictions

    workation_rank = pd.read_csv(download_folder + '/워케이션 순위.csv', encoding='CP949')
    kor_to_eng_map = dict(zip(workation_rank['SIG_KOR_NM'], workation_rank['SIG_ENG_NM']))

    top_3_regions = results_df[kw_list].mean().nlargest(3).index.tolist()
    top_3_regions_eng = [kor_to_eng_map[name] for name in top_3_regions]

    kw_recommend = [{'locationName': top_3_regions_eng[0].split('-')[0],
                     'ranking': 1},
                    {'locationName': top_3_regions_eng[1].split('-')[0],
                     'ranking': 2},
                    {'locationName': top_3_regions_eng[2].split('-')[0],
                     'ranking': 3}]

    return kw_recommend
