package com.example.mdmjive

import android.app.NotificationManager
import android.content.Context
import androidx.test.core.app.ServiceScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.mdmjive.services.MDMService
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MDMServiceTest {
    @Test
    fun baseUrlIsConfigurable() {
        assertTrue(BuildConfig.MDM_SERVER_URL.isNotEmpty())
    }

    @Test
    fun serviceShowsForegroundNotification() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        ServiceScenario.launch(MDMService::class.java).use {
            val active = notificationManager.activeNotifications.any { it.id == MDMService.FOREGROUND_ID }
            assertTrue(active)
        }
    }
}
