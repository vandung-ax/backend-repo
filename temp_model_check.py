from catboost import CatBoostClassifier
m = CatBoostClassifier()
m.load_model('ml_models/catboost_model.cbm')
print('feature_names:', m.feature_names_)
print('cat:', m.get_cat_feature_indices())
