package com.example.mdmjive

import android.content.Context
import android.provider.Settings
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.mdmjive.database.LogDatabase
import com.example.mdmjive.network.ApiService
import com.example.mdmjive.network.models.ApiResponse
import com.example.mdmjive.repository.DeviceRepository
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import retrofit2.Response
import kotlin.test.assertNotNull

@RunWith(AndroidJUnit4::class)
class DeviceRegistrationInstrumentedTest {
    private lateinit var context: Context
    private lateinit var db: LogDatabase
    private lateinit var api: ApiService
    private lateinit var repository: DeviceRepository

    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
        Settings.Secure.putString(context.contentResolver, Settings.Secure.ANDROID_ID, "android-device")
        db = Room.inMemoryDatabaseBuilder(context, LogDatabase::class.java).build()
        api = mock()
        repository = DeviceRepository(api, db.deviceDao())
    }

    @After
    fun tearDown() {
        db.close()
    }

    @Test
    fun registerDevice_insertsRecordInDatabase() = runBlocking {
        whenever(api.registerDevice(any())).thenReturn(Response.success(ApiResponse(true)))
        repository.registerDevice(context)
        val stored = db.deviceDao().getDevice("android-device")
        assertNotNull(stored)
    }
}

