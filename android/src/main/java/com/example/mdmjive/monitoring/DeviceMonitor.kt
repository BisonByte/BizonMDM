package com.example.mdmjive.monitoring

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Environment
import android.os.StatFs

class DeviceMonitor(private val context: Context) {

    fun getBatteryStatus(): BatteryInfo {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))

        return BatteryInfo(
            level = calculateBatteryLevel(batteryIntent),
            isCharging = isCharging(batteryIntent),
            temperature = batteryIntent?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0
        )
    }

    fun getNetworkStatus(): NetworkInfo {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val networkCapabilities = connectivityManager.getNetworkCapabilities(connectivityManager.activeNetwork)

        return NetworkInfo(
            isConnected = networkCapabilities != null,
            type = when {
                networkCapabilities?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true -> "Wi-Fi"
                networkCapabilities?.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) == true -> "Cellular"
                networkCapabilities?.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) == true -> "Ethernet"
                else -> "Unknown"
            }
        )
    }

    fun getStorageInfo(): StorageInfo {
        val stat = StatFs(Environment.getDataDirectory().path)
        val totalSpace = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.JELLY_BEAN_MR2) {
            stat.totalBytes
        } else {
            stat.blockCountLong * stat.blockSizeLong
        }

        val freeSpace = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.JELLY_BEAN_MR2) {
            stat.freeBytes
        } else {
            stat.availableBlocksLong * stat.blockSizeLong
        }

        return StorageInfo(
            totalSpace = totalSpace,
            freeSpace = freeSpace,
            usedSpace = totalSpace - freeSpace
        )
    }

    private fun calculateBatteryLevel(intent: Intent?): Int {
        return intent?.let { batteryIntent ->
            val level = batteryIntent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = batteryIntent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            if (level != -1 && scale != -1) {
                level * 100 / scale
            } else {
                -1
            }
        } ?: -1
    }

    private fun isCharging(intent: Intent?): Boolean {
        return intent?.getIntExtra(BatteryManager.EXTRA_STATUS, -1)?.let { status ->
            status == BatteryManager.BATTERY_STATUS_CHARGING || status == BatteryManager.BATTERY_STATUS_FULL
        } ?: false
    }
}

data class BatteryInfo(
    val level: Int,
    val isCharging: Boolean,
    val temperature: Int
)

data class NetworkInfo(
    val isConnected: Boolean,
    val type: String
)

data class StorageInfo(
    val totalSpace: Long,
    val freeSpace: Long,
    val usedSpace: Long
)
