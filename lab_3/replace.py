def replace_function(data_frames):
        province_ID_dictionary = {
            16: 13,
            27: 5, 
            10: 21, 
            3: 23, 
            11: 9,
            25: 2,
            17: 14,
            21: 17,
            1: 22,    
            18: 15,
            6: 4,
            9: 20,   
            8: 19,
            19: 16,
            23: 6,
            7: 8,
            5: 3,
            26: 7,
            2: 24,
            4: 25,
            15: 11,
            22: 18,
            13: 10,
            24: 1,
            14: 12,
        }    
        
        data_frames_work = data_frames.copy()
        data_frames_work = data_frames_work.replace({"PROVINCE_ID": province_ID_dictionary})   
        
        return data_frames_work