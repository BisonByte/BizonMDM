package com.example.mdmjive

import android.app.Service
import android.content.Intent
import androidx.test.core.app.ApplicationProvider
import com.example.mdmjive.services.MDMService
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import kotlin.test.assertEquals

@RunWith(RobolectricTestRunner::class)
class MDMServiceTest {
    @Test
    fun onStartCommand_returnsStartSticky() {
        val service = Robolectric.buildService(MDMService::class.java).create().get()
        val intent = Intent(ApplicationProvider.getApplicationContext(), MDMService::class.java)
        val result = service.onStartCommand(intent, 0, 0)
        assertEquals(Service.START_STICKY, result)
    }
}

