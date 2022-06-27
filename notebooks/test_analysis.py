from common.statistics import AnalyzeStar

analysis = AnalyzeStar(7)
analysis.load_data()
result = analysis.process_stars()
print(result)
result.to_csv('test_analysis.csv')