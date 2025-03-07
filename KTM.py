import math

class LZ77_compressor:
    DICTIONARY_SIZE = 3
    CODING_SIZE = 4 # look ahead buffor
    
    def Find_Longest_Prefix(self, input_bytes, current_index):
        longest_prefix = (0, 0) # (distance, length)

        # lecę od tyłu do indexu
        for i in range(max(0, current_index - self.DICTIONARY_SIZE), current_index):
            j = 0
            while(current_index + j < len(input_bytes) and
                  j < self.CODING_SIZE and
                  input_bytes[i + j] == input_bytes[current_index + j]):
                j += 1
            
            if j > longest_prefix[1]:
                longest_prefix = (current_index - i, j)
                
        return longest_prefix

    
    def Encode(self, input_bytes):
        compressed_list = []
        current_index = 0
        
        while(current_index < len(input_bytes)):
            token = self.Find_Longest_Prefix(input_bytes, current_index)
            
            # the first value of token is a flag
            if token[1] > 0:
                compressed_list.append((1, token[1], token[0]))
                current_index += token[1]
            else:
                compressed_list.append((0, input_bytes[current_index]))
                current_index += 1

        return compressed_list
    
    
    def Decode(self, compressed_data):
        decompressed_lsit = []
        
        for token in compressed_data:
            if token[0] == 0:
                decompressed_lsit.append(token[1])
            else:
                start_index = len(decompressed_lsit) - token[2]
                end_index = start_index + token[1]
                # decompressed_lsit.append(decompressed_lsit[start_index:end_index])
                for i in range(start_index, end_index):
                    decompressed_lsit.append(decompressed_lsit[i])
        return decompressed_lsit
    

    def Compress(self, input_path, output_path, verbose='True'):
        bytes_data = []
        try:
            with open(input_path, 'rb') as input_file:
                while(byte := input_file.read(1)):
                    bytes_data.append(byte)
        except IOError:
            print('Could not open input file ...')
            raise
        
        encoded = self.Encode(bytes_data)
        
        
        
        prepared_bytes = [] # tokens prepared to be printed to file
        
        for token in encoded:
            if token[0] == 0: # if not in dict then just append 0 and the byte
                prepared_bytes.append((0).to_bytes())
                prepared_bytes.append(token[1])
            elif token[0] == 1:
                prepared_bytes.append((1).to_bytes())
                prepared_bytes.append(token[1].to_bytes())
                prepared_bytes.append(token[2].to_bytes())
            else:
                print("Error: Wrong flag: ", token[0])
                return 1
  
        with open(output_path, 'wb') as output_file:
            for byte in prepared_bytes:
                output_file.write(byte)
                
        if verbose:
            # collecting information about compression
            input_length = len(bytes_data)
            encoded_length = len(prepared_bytes)
            compression_ratio = encoded_length / input_length
            input_weights = [0] * 256 # one slot for each possible byte
            for byte in bytes_data:
                input_weights[int.from_bytes(byte)] += 1
            encoded_weights = [0] * 256
            for byte in prepared_bytes:
                encoded_weights[int.from_bytes(byte)] += 1               
                
            # calculating entropys
            input_entropy = 0
            for w in input_weights:
                if w != 0:
                    input_entropy -= (w / input_length) * math.log(w / input_length)
            encoded_entropy = 0 
            for c in encoded_weights:
                if c != 0:
                    encoded_entropy -= (c / encoded_length) * math.log(c / encoded_length)             
        
            print("text length: ", input_length)
            print("encoded length: ", encoded_length)
            print("compression ratio: ", compression_ratio)
            print("text entropy: ", input_entropy)
            print("encoded entropy: ", encoded_entropy)
        
        return prepared_bytes


    def Decompress(self, input_path, output_path):
        input_bytes = []
        with open(input_path, "rb") as input_file:
            while(byte := input_file.read(1)):
                input_bytes.append(byte)  
                
        # making tokens from bytes
        tokens = []
        
        i = 0
        while i < len(input_bytes):
            flag = input_bytes[i]
            if flag == b'\x00':
                tokens.append((0, input_bytes[i+1]))
                i += 2
            elif flag == b'\x01':
                tokens.append((1, int.from_bytes(input_bytes[i+1]),
                               int.from_bytes(input_bytes[i+2])))
                i += 3
            else:
                print("Error: Wrong flag: ", int.from_bytes(flag))
                
        decoded = self.Decode(tokens)
        with open(output_path, 'wb') as output_file:
            for byte in decoded:
                output_file.write(byte)     
        
        return decoded
        
    
    


# char_input = bytes.decode(read_input, "utf-8")

#
