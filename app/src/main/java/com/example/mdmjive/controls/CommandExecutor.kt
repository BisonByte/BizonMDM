package com.example.mdmjive.controls

import android.app.admin.DevicePolicyManager
import android.app.WallpaperManager
import android.content.ComponentName
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.annotation.RequiresApi
import android.graphics.Bitmap
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Executors
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
                "factory_reset" -> factoryReset()
                "reboot" -> rebootDevice()
                "screenshot" -> captureScreenshot()
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

    fun factoryReset() {
        try {
            dpm.wipeData(0)
        } catch (e: Exception) {
            Log.e("CommandExecutor", "Error realizando factory reset", e)
        }
    }

    @RequiresApi(Build.VERSION_CODES.N)
    fun rebootDevice() {
        try {
            dpm.reboot(componentName)
        } catch (e: Exception) {
            Log.e("CommandExecutor", "Error reiniciando dispositivo", e)
        }
    }

    fun captureScreenshot() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val executor = Executors.newSingleThreadExecutor()
                dpm.takeScreenshot(componentName, executor) { bitmap ->
                    try {
                        val file = File(
                            context.getExternalFilesDir(null),
                            "screenshot_${System.currentTimeMillis()}.png"
                        )
                        FileOutputStream(file).use { out ->
                            bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, out)
                        }
                        Log.d("CommandExecutor", "Captura guardada en ${'$'}{file.absolutePath}")
                    } catch (e: Exception) {
                        Log.e("CommandExecutor", "Error guardando captura", e)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e("CommandExecutor", "Error capturando pantalla", e)
        }
    }
}
