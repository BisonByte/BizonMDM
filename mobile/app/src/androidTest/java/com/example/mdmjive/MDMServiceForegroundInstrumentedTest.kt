package com.example.mdmjive

import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.mdmjive.services.MDMService
import org.junit.Test
import org.junit.runner.RunWith
import kotlin.test.assertTrue

@RunWith(AndroidJUnit4::class)
class MDMServiceForegroundInstrumentedTest {
    @Test
    fun startingService_postsForegroundNotification() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        context.startForegroundService(Intent(context, MDMService::class.java))
        Thread.sleep(1000)
        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val active = manager.activeNotifications.any { it.id == MDMService.NOTIFICATION_ID }
        assertTrue(active)
    }
}
