#!/usr/bin/env python
# coding: utf-8
def postfilter_items(user, data, data1, obj, col, N):
    # 2 новых товара (юзер никогда не покупал)
    # 1 дорогой товар, > 7 долларов (price = sum(sales_value) / sum(quantity))
    # Все товары из разных категорий (категория - sub_commodity_desc)
    
      
    bought_list = data.loc[data['user_id']==user, 'actual'].values[0]
    recommendations = data.loc[data['user_id']==user, col].values[0]
    exp_item = obj.item_mean_cost.loc[obj.item_mean_cost['mean_price'] > 7,'item_id'].values
    
    if user in obj.userid_to_id:
        all_rec = obj.all_recommendations[obj.userid_to_id[user]]
    else:
        all_rec = []
        
    # Разные категории
    categories_used = []
    different_categories = []
    CATEGORY_NAME = 'sub_commodity_desc'
    
    expensive_product = []
    pos_expensive_product = []
    item_expensive_product = []
    
    new_product = []
    pos_new_product = []
    item_new_product = []
    
    unique_recommendations = []
    
    # Уникальность   
    for i in range(len(recommendations)):
        item = recommendations[i]
        if item not in unique_recommendations:
            unique_recommendations.append(item)
            
        
#         if (i<len(data.loc[data['user_id']==user, 'bm25_als'].values[0])):
#             item = data.loc[data['user_id']==user, 'bm25_als'].values[0][i]
#             if (item not in unique_recommendations):
#                 unique_recommendations.append(item)
    
    for i in range(len(all_rec)):
        if (i<len(all_rec)):
            item = obj.id_to_itemid[all_rec[i]]
            if (item not in unique_recommendations):
                unique_recommendations.append(item)

    if len(unique_recommendations) == 0:
        return []
    
#     unique_recommendations = []
#     unique_recommendations.append(unique_recommendations_all[0])
#     for item in unique_recommendations_all[1:]:
#         if item_mean_cost.loc[item_mean_cost['item_id'] == item,'mean_price'].values[0] > 2:
#             unique_recommendations.append(item)
                

    # 1 дорогой товар, > 7 долларов
    i = 0
    for item in unique_recommendations:
        if item in exp_item:
            expensive_product.append(item)
            category = obj.item_features.loc[obj.item_features['item_id'] == item, CATEGORY_NAME].values[0]
            categories_used.append(category)
            unique_recommendations.remove(item)
            break
#         if i == 15:
#             break
#         i+=1

#     categories_used = item_features.loc[item_features['item_id'].isin(different_categories[:2]), CATEGORY_NAME].values
    if len(expensive_product)==0:
        expensive_product.append(obj.popular_exp_item)
        category = obj.item_features.loc[obj.item_features['item_id'] == obj.popular_exp_item, CATEGORY_NAME].values[0]
        categories_used.append(category)

        
    # 2 новых товара (юзер никогда не покупал)
    i = 0
    for item in unique_recommendations:
#         print(user, item)
        category = obj.item_features.loc[obj.item_features['item_id'] == item, CATEGORY_NAME].values[0]
        if (not item in bought_list) & (category not in categories_used):
            new_product.append(item)
            categories_used.append(category)
            unique_recommendations.remove(item)                                          
#         if i == 15:
#             break
#         i+=1
        if len(new_product) == 2:
            break       
            
    if len(new_product)<2:
        for item in top:
            category = obj.item_features.loc[obj.item_features['item_id'] == item, CATEGORY_NAME].values[0]
            if (not item in bought_list) & (category not in categories_used):
                new_product.append(item)        
            if len(new_product) == 2:
                break          
               
        
    for item in unique_recommendations:
#         print(user, item)
        category = obj.item_features.loc[obj.item_features['item_id'] == item, CATEGORY_NAME].values[0]

        if category not in categories_used:
            different_categories.append(item)

        unique_recommendations.remove(item)
        categories_used.append(category)
        
        
    final_recommendations = different_categories[:2] + new_product[:2] + expensive_product[:1]
    if len(expensive_product) < 1:
        print('нет expensive_product', user)
    if len(new_product) < 2:
        print('нет new_product', user)
    return final_recommendations

def prefilter_items(data, take_n_popular, item_mean_cost):
#     """Предфильтрация товаров"""  
     
    # 4. Выбор топ-N самых популярных товаров (N = take_n_popular)  
    # 0.176 важно запустить до обрезки цены
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.sort_values('quantity', ascending=False, inplace=True)
    top_popular = popularity.head(20).item_id.tolist()
    data = data[~data['item_id'].isin(top_popular)]
    print(data['item_id'].nunique())
    
    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity.loc[popularity['quantity']<10].item_id.tolist()
    data = data[~data['item_id'].isin(top_notpopular)]
    print(data['item_id'].nunique())
    
    # 1. Удаление товаров, со средней ценой < 2$
    data = data[data['sales_value'] / data['quantity'] > 2]
    print(data['item_id'].nunique())
    

    return data, top_popular