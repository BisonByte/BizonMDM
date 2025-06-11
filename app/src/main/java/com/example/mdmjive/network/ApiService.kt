package com.example.mdmjive.network

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import android.util.Log
import com.example.mdmjive.network.models.ApiResponse
import com.example.mdmjive.network.models.DeviceInfo
import com.example.mdmjive.network.models.DeviceStatus
import com.example.mdmjive.network.models.LogPayload

// Interface para los endpoints de la API
interface ApiService {
    @POST("devices/register")
    suspend fun registerDevice(@Body deviceInfo: DeviceInfo): Response<ApiResponse>

    @POST("devices/status")
    suspend fun updateStatus(@Body status: DeviceStatus): Response<ApiResponse>

    @POST("logs")
    suspend fun uploadLogs(@Body payload: LogPayload): Response<ApiResponse>
}



// Clase para manejar las respuestas de la API de manera segura
sealed class ApiResult<out T> {
    data class Success<out T>(val data: T) : ApiResult<T>()
    data class Error(val exception: Exception) : ApiResult<Nothing>()
}

object ApiHandler {
    suspend fun <T> safeApiCall(
        call: suspend () -> Response<T>
    ): ApiResult<T> {
        return try {
            val response = call()
            if (response.isSuccessful) {
                response.body()?.let {
                    ApiResult.Success(it)
                } ?: ApiResult.Error(Exception("Response body is null"))
            } else {
                ApiResult.Error(Exception("API call failed with code: ${response.code()}"))
            }
        } catch (e: Exception) {
            Log.e("ApiHandler", "API call failed", e)
            ApiResult.Error(e)
        }
    }
}

// Clase para manejar las operaciones del dispositivo
class DeviceOperations(private val apiService: ApiService) {
    suspend fun registerDeviceAndUpdateStatus(
        deviceInfo: DeviceInfo,
        deviceStatus: DeviceStatus
    ): ApiResult<Boolean> {
        return try {
            when (val registerResult = ApiHandler.safeApiCall { apiService.registerDevice(deviceInfo) }) {
                is ApiResult.Success -> {
                    if (registerResult.data.success) {
                        when (val statusResult = ApiHandler.safeApiCall { apiService.updateStatus(deviceStatus) }) {
                            is ApiResult.Success -> {
                                ApiResult.Success(true)
                            }
                            is ApiResult.Error -> {
                                Log.e("DeviceOperations", "Failed to update status", statusResult.exception)
                                ApiResult.Error(statusResult.exception)
                            }
                        }
                    } else {
                        ApiResult.Error(Exception("Device registration failed"))
                    }
                }
                is ApiResult.Error -> {
                    Log.e("DeviceOperations", "Failed to register device", registerResult.exception)
                    ApiResult.Error(registerResult.exception)
                }
            }
        } catch (e: Exception) {
            Log.e("DeviceOperations", "Operation failed", e)
            ApiResult.Error(e)
        }
    }
}

object ApiServiceFactory {
    fun create(baseUrl: String): ApiService {
        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        return retrofit.create(ApiService::class.java)
    }
}