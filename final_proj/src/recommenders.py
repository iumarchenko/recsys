#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np

# Для работы с матрицами
from scipy.sparse import csr_matrix

# Матричная факторизация
from implicit.als import AlternatingLeastSquares
from implicit.nearest_neighbours import ItemItemRecommender  # нужен для одного трюка
from implicit.nearest_neighbours import bm25_weight, tfidf_weight


class MainRecommender:
    """Рекоммендации, которые можно получить из ALS
    
    Input
    -----
    user_item_matrix: pd.DataFrame
        Матрица взаимодействий user-item
    """
    
    def __init__(self, data, top_popular, item_features, item_mean_cost, popular_exp_item, weighting=True):
                
        # Топ покупок каждого юзера
        self.top_popular = top_popular
        self.item_features = item_features
        self.item_mean_cost = item_mean_cost
        self.popular_exp_item = popular_exp_item
        
        self.user_item_matrix = self.prepare_matrix(data)  # pd.DataFrame
        self.id_to_itemid, self.id_to_userid, self.itemid_to_id, self.userid_to_id = self.prepare_dicts(self.user_item_matrix)
        
        
        if weighting:
            self.user_item_matrix = bm25_weight(self.user_item_matrix.T, K1=12,B=0.165).T 
        
        self.model = self.fit(self.user_item_matrix)
        
        self.own_recommender = self.fit_own_recommender(self.user_item_matrix)
     
        self.all_recommendations = self.get_all_recommendations(self.model,N=200)
        
    @staticmethod
    def prepare_matrix(data):
        #your_code
        user_item_matrix = pd.pivot_table(data, 
                                  index='user_id', columns='item_id', 
                                  values='quantity', # Можно пробоват ьдругие варианты
                                  aggfunc='count', 
                                  fill_value=0
                                 )

        user_item_matrix = user_item_matrix.astype(float)
        
        return user_item_matrix
    
    @staticmethod
    def prepare_dicts(user_item_matrix):
        """Подготавливает вспомогательные словари"""
        
        userids = user_item_matrix.index.values
        itemids = user_item_matrix.columns.values

        matrix_userids = np.arange(len(userids))
        matrix_itemids = np.arange(len(itemids))

        id_to_itemid = dict(zip(matrix_itemids, itemids))
        id_to_userid = dict(zip(matrix_userids, userids))

        itemid_to_id = dict(zip(itemids, matrix_itemids))
        userid_to_id = dict(zip(userids, matrix_userids))
        
        return id_to_itemid, id_to_userid, itemid_to_id, userid_to_id
     
    @staticmethod
    def fit_own_recommender(user_item_matrix):
        """Обучает модель, которая рекомендует товары, среди товаров, купленных юзером"""
    
        own_recommender = ItemItemRecommender(K=1, num_threads=8)
        own_recommender.fit(csr_matrix(user_item_matrix).T.tocsr(),show_progress=True)
                    
        return own_recommender
    
    @staticmethod
    def fit(user_item_matrix, n_factors=20, regularization=0.001, iterations=15, num_threads=4):
        """Обучает ALS"""
               
        model = AlternatingLeastSquares(factors=7, 
                                regularization=0.001,
                                iterations=15, 
                                calculate_training_loss=True, 
                                num_threads=16)
        model.fit(csr_matrix(user_item_matrix).T.tocsr())
        
        return model      
       

    def get_all_recommendations(self, model, N=200):
        recommendations = model.recommend_all(N=N, 
                                              user_items=csr_matrix(self.user_item_matrix).tocsr(),
                                              filter_already_liked_items=True, 
                                              filter_items=False, 
                                              recalculate_user=True,
                                              show_progress=True,
                                              batch_size=500)
        return recommendations

    def get_recommendations(self, user, model, N=5):
        res = []
        if user in self.userid_to_id:
            res = [self.id_to_itemid[rec[0]] for rec in 
                            model.recommend(userid=self.userid_to_id[user], 
                                            user_items=csr_matrix(self.user_item_matrix).tocsr(),   # на вход user-item matrix
                                            N=N, 
                                            filter_already_liked_items=False, 
                                            filter_items=False,  
                                            recalculate_user=False)]
        return res
        
    def get_recommendations_price(self, recommendations):
        res = [self.item_mean_cost.loc[self.item_mean_cost['item_id']==pr,'mean_price'].values[0] for pr in recommendations]
        return res
        