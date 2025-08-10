package com.example.mdmjive.receivers

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Settings
import android.util.Log
import com.example.mdmjive.BuildConfig
import com.example.mdmjive.network.ApiServiceFactory
import com.example.mdmjive.network.models.DeviceStatus
import kotlinx.coroutines.runBlocking
import java.io.File
import com.example.mdmjive.utils.TokenManager

class SecurityEventReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val sentinel = File(context.filesDir, "sentinel")
        val wipeDetected = !sentinel.exists()
        if (wipeDetected) {
            try {
                sentinel.createNewFile()
            } catch (e: Exception) {
                Log.e("SecurityEventReceiver", "Failed to create sentinel", e)
            }
        }

        val bootState = getSystemProperty("ro.boot.verifiedbootstate")
        val bootloaderTampered = bootState.isNotEmpty() && bootState != "green"

        val deviceId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        val api = ApiServiceFactory.create(BuildConfig.BASE_URL)
        val status = DeviceStatus(
            deviceId = deviceId,
            status = "OK",
            wipeDetected = wipeDetected,
            bootloaderTampered = bootloaderTampered
        )
        val token = TokenManager.getToken(context)
        if (token != null) {
            try {
                val bearer = "Bearer $token"
                runBlocking { api.updateStatus(bearer, status) }
            } catch (e: Exception) {
                Log.e("SecurityEventReceiver", "Failed to send status", e)
            }
        } else {
            Log.e("SecurityEventReceiver", "Token no disponible")
        }
    }

    private fun getSystemProperty(name: String): String {
        return try {
            val cls = Class.forName("android.os.SystemProperties")
            val method = cls.getMethod("get", String::class.java)
            method.invoke(null, name) as String
        } catch (e: Exception) {
            ""
        }
    }
}
