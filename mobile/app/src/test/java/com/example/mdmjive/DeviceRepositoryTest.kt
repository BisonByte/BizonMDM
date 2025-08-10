package com.example.mdmjive

import android.content.Context
import android.provider.Settings
import androidx.test.core.app.ApplicationProvider
import com.example.mdmjive.database.dao.DeviceDao
import com.example.mdmjive.network.ApiService
import com.example.mdmjive.network.models.ApiResponse
import com.example.mdmjive.network.models.Command
import com.example.mdmjive.repository.DeviceRepository
import kotlinx.coroutines.runBlocking
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.mockito.kotlin.*
import retrofit2.Response
import kotlin.test.assertEquals

@RunWith(RobolectricTestRunner::class)
class DeviceRepositoryTest {
    private lateinit var apiService: ApiService
    private lateinit var deviceDao: DeviceDao
    private lateinit var repository: DeviceRepository
    private lateinit var context: Context

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        Settings.Secure.putString(context.contentResolver, Settings.Secure.ANDROID_ID, "test-device")
        apiService = mock()
        deviceDao = mock()
        repository = DeviceRepository(apiService, deviceDao)
    }

    @Test
    fun updateDeviceStatus_updatesDaoOnSuccess() = runBlocking {
        whenever(apiService.updateStatus(any())).thenReturn(Response.success(ApiResponse(true)))
        repository.updateDeviceStatus(context, "ACTIVE")
        verify(deviceDao).updateDeviceStatus(eq("test-device"), eq("ACTIVE"), any())
    }

    @Test
    fun fetchCommands_returnsCommandsFromApi() = runBlocking {
        whenever(apiService.getCommands()).thenReturn(Response.success(listOf(Command("LOCK"))))
        val result = repository.fetchCommands(context)
        assertEquals(1, result.size)
        assertEquals("LOCK", result.first().action)
    }
}

