package com.example.mdmjive

import com.example.mdmjive.network.ApiHandler
import com.example.mdmjive.network.ApiResult
import kotlinx.coroutines.runBlocking
import org.junit.Test
import kotlin.test.assertTrue
import retrofit2.Response

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
}

