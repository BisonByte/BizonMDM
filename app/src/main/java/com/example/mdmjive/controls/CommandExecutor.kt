package com.example.mdmjive.controls

import android.app.admin.DevicePolicyManager
import android.app.WallpaperManager
import android.content.ComponentName
import android.content.Context
import android.content.pm.PackageManager
import android.util.Log
import android.widget.Toast
import com.example.mdmjive.R
import com.example.mdmjive.network.models.Command
import com.example.mdmjive.receivers.MDMDeviceAdminReceiver

class CommandExecutor(private val context: Context) {
    private val dpm = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
    private val componentName = ComponentName(context, MDMDeviceAdminReceiver::class.java)
    private val pm: PackageManager = context.packageManager

    fun execute(commands: List<Command>) {
        commands.forEach { cmd ->
            when (cmd.action) {
                "hide_app" -> cmd.packageName?.let { hideApp(it) }
                "hide_all_apps" -> hideAllApps()
                "lock_device" -> lockDevice(cmd.message)
            }
        }
    }

    fun hideApp(packageName: String) {
        try {
            dpm.setApplicationHidden(componentName, packageName, true)
            Toast.makeText(context, "App $packageName ocultada", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Log.e("CommandExecutor", "Error ocultando app", e)
        }
    }

    fun hideAllApps() {
        try {
            val packages = pm.getInstalledPackages(0)
            packages.forEach { pkg ->
                if (pkg.packageName != context.packageName) {
                    try {
                        dpm.setApplicationHidden(componentName, pkg.packageName, true)
                    } catch (_: Exception) { }
                }
            }
            Toast.makeText(context, "Todas las apps ocultadas", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Log.e("CommandExecutor", "Error ocultando todas las apps", e)
        }
    }

    fun lockDevice(message: String?) {
        try {
            val wallpaperManager = WallpaperManager.getInstance(context)
            wallpaperManager.setResource(R.drawable.lock_wallpaper)
            message?.let { Toast.makeText(context, it, Toast.LENGTH_LONG).show() }
            dpm.lockNow()
        } catch (e: Exception) {
            Log.e("CommandExecutor", "Error bloqueando dispositivo", e)
        }
    }
}
