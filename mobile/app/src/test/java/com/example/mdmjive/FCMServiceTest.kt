package com.example.mdmjive

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.mdmjive.services.FCMService
import com.example.mdmjive.utils.TokenManager
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import kotlin.test.assertEquals

@RunWith(RobolectricTestRunner::class)
class FCMServiceTest {
    @Test
    fun onNewToken_savesToken() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val service = Robolectric.buildService(FCMService::class.java).create().get()
        service.onNewToken("abc123")
        val saved = TokenManager.getToken(context)
        assertEquals("abc123", saved)
    }
}
