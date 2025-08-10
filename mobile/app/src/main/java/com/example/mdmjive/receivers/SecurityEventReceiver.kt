package com.example.mdmjive.receivers

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.example.mdmjive.BuildConfig
import com.example.mdmjive.database.LogDatabase
import com.example.mdmjive.network.ApiServiceFactory
import com.example.mdmjive.repository.DeviceRepository
import java.io.File

class SecurityEventReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        Log.d("SecurityEventReceiver", "Received ${intent.action}")

        val sentinel = File(context.filesDir, "boot_sentinel")
        val wipeDetected = !sentinel.exists()
        if (wipeDetected) {
            try {
                sentinel.createNewFile()
            } catch (_: Exception) {
            }
        }

        val bootState = getVerifiedBootState()
        val bootloaderTampered = bootState.isNotEmpty() && bootState != "green"

        val repository = DeviceRepository(
            ApiServiceFactory.create(BuildConfig.BASE_URL),
            LogDatabase.getDatabase(context).deviceDao()
        )
        try {
            repository.reportSecurityEvent(context, wipeDetected, bootloaderTampered)
        } catch (e: Exception) {
            Log.e("SecurityEventReceiver", "Error sending security event: ${e.localizedMessage}")
        }
    }

    private fun getVerifiedBootState(): String {
        return try {
            val clazz = Class.forName("android.os.SystemProperties")
            val method = clazz.getMethod("get", String::class.java, String::class.java)
            method.invoke(null, "ro.boot.verifiedbootstate", "") as String
        } catch (e: Exception) {
            ""
        }
    }
}
