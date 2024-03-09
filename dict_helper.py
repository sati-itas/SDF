def merge_multi(dict_array):
        """merges multiple dicts respecting keys and values, that already exists (no overwriting)

        Args:
            dict_array (_type_): _description_

        Returns:
            _type_: _description_
        """
        dictx = merge_dicts(dict_array[0], dict_array[1])
        for dict_number in range(2,len(dict_array)):
                dictx = merge_dicts(dictx, dict_array[dict_number])
        return dictx    


def merge_dicts(dict1, dict2):
        """merges 2 dicts with respect of keys and values that are already in dict (no overwriting)

        Args:
            dict1 (_type_): _description_
            dict2 (_type_): _description_

        Returns:
            _type_: _description_
        """
        dict2_liste=[]
        merged_dict={**{}, **dict1}
        for key2 in dict2:
                for item2 in dict2[key2]:
                        if isinstance(item2, list):
                                dict2_liste.append(item2)
                        else: 
                                dict2_liste.append(item2)   
               
                try:
                        if isinstance(merged_dict[key2][0], list):
                                for listitem in dict2_liste:
                                        if isinstance(listitem, list):
                                                merged_dict[key2].append(listitem)
                                        else:
                                                merged_dict[key2].append(dict2_liste)
                                                break 
                                dict2_liste=[]
                        else:
                                merged_dict[key2]=[merged_dict[key2]]
                                for listitem in dict2_liste:
                                        if isinstance(listitem, list):
                                                merged_dict[key2].append(listitem)
                                        else:
                                                merged_dict[key2].append(dict2_liste)
                                                break
                except: 
                        merged_dict.update({key2:dict2_liste})        
                dict2_liste=[]

        return merged_dict