package com.example.mdmjive

import com.example.mdmjive.network.ApiHandler
import com.example.mdmjive.network.ApiResult
import kotlinx.coroutines.runBlocking
import org.junit.Test
import kotlin.test.assertTrue
import retrofit2.Response
import okhttp3.ResponseBody
import okhttp3.MediaType.Companion.toMediaTypeOrNull

class ApiServiceTest {
    @Test
    fun safeApiCall_returnsSuccess() = runBlocking {
        val result = ApiHandler.safeApiCall { Response.success("ok") }
        assertTrue(result is ApiResult.Success && result.data == "ok")
    }

    @Test
    fun safeApiCall_handlesException() = runBlocking {
        val result = ApiHandler.safeApiCall<String> { throw RuntimeException("boom") }
        assertTrue(result is ApiResult.Error)
    }

    @Test
    fun safeApiCall_handlesHttpError() = runBlocking {
        val body = ResponseBody.create("text/plain".toMediaTypeOrNull(), "not found")
        val result = ApiHandler.safeApiCall<String> { Response.error(404, body) }
        assertTrue(result is ApiResult.Error)
    }
}

