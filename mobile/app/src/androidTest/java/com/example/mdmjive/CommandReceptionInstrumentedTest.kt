package com.example.mdmjive

import android.content.Context
import android.provider.Settings
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.mdmjive.network.ApiService
import com.example.mdmjive.network.models.Command
import com.example.mdmjive.repository.DeviceRepository
import kotlinx.coroutines.runBlocking
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import retrofit2.Response
import kotlin.test.assertEquals

@RunWith(AndroidJUnit4::class)
class CommandReceptionInstrumentedTest {
    private lateinit var context: Context
    private lateinit var api: ApiService
    private lateinit var repository: DeviceRepository

    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
        Settings.Secure.putString(context.contentResolver, Settings.Secure.ANDROID_ID, "android-device")
        api = mock()
        val dao = mock<com.example.mdmjive.database.dao.DeviceDao>()
        repository = DeviceRepository(api, dao)
    }

    @Test
    fun fetchCommands_returnsListFromApi() = runBlocking {
        whenever(api.getCommands("android-device")).thenReturn(Response.success(listOf(Command("LOCK"))))
        val commands = repository.fetchCommands(context)
        assertEquals(1, commands.size)
        assertEquals("LOCK", commands[0].action)
    }
}

