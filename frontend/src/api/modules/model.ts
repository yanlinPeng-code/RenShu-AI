import request from '../request';
import type {
  ApiResponse,
  ModelConfigCreate,
  ModelConfigUpdate,
  ModelProviderCreate,
  ModelProviderUpdate,
  ModelProviderDelete,
  ModelConfigDelete,
  ProviderApiKeyVerify
} from '../types';
// 提供商管理api
export const providerApi = {
       create:(data:ModelProviderCreate): Promise<ApiResponse<any>> => {
            return request.post('/api/v1/provider/create',data);

        },
        update:(data:ModelProviderUpdate ):Promise<ApiResponse<any>> => {
            return request.post('/api/v1/provider/update',data);
        },
        delete:(data:ModelProviderDelete):Promise<ApiResponse<any>> => {
            return request.post(`/api/v1/provider/delete`,data);
        },
        verifyApiKey:(data:ProviderApiKeyVerify):Promise<ApiResponse<any>> => {
            return request.post('/api/v1/provider/verify_api_key',data);
        },
        //共用提供商和模型管理
       get_providers_with_models:():Promise<ApiResponse<any>> => {
            return request.get(`/api/v1/providers_with_models`);
        },
       get_builtin_providers_with_models:():Promise<ApiResponse<any>> => {
            return request.get(`/api/v1/builtin/providers_with_models`);
        },







}


// 模型管理api
export const modelApi = {
       
       //管理员配置模型
       create:(data:ModelConfigCreate):Promise<ApiResponse<any>> => {
            return request.post('/api/v1/model/config/create',data)
        },
        update:(data: ModelConfigUpdate):Promise<ApiResponse<any>> =>{
            return request.post('/api/v1/model/config/update',data)
        },
        delete:(data:ModelConfigDelete):Promise<ApiResponse<any>> =>{
            return request.post(`/api/v1/model/config/delete`,data)
        },
        // //用户模型管理
        // user_create:(data:UserModelConfigCreate):Promise<ApiResponse<any>> =>{
        //     return request.post('/api/v1/user/model/config/create',data)
        // },
        // user_update:(data: UserModelConfigUpdate):Promise<ApiResponse<any>> =>{
        //     return request.post('/api/v1/user/model/config/update',data)
        // },
        // user_delete:(data:ModelConfigDelete):Promise<ApiResponse<any>> =>{
        //     return request.post(`/api/v1/user/model/config/delete`,data)
        // },
        // user_get:():Promise<ApiResponse<any>> =>{
        //     return request.get(`/api/v1/user/get/model/configs`)
        // },
        // user_set_default:(config_id:string):Promise<ApiResponse<any>> =>{
        //     return request.post(`/api/v1/user/set/model/config/default/${config_id}`)
        // },





} 