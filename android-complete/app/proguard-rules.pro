# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# Uncomment this to preserve the line number information for
# debugging stack traces.
#-keepattributes SourceFile,LineNumberTable

# If you keep the line number information, uncomment this to
# hide the original source file name.
#-renamesourcefileattribute SourceFile

# Capacitor plugin classes
-keep class com.getcapacitor.** { *; }
-keep class com.capacitorjs.** { *; }

# AWS SDK classes
-keep class com.amazonaws.** { *; }
-keep class com.amazon.** { *; }

# Google Play Billing classes
-keep class com.android.billingclient.** { *; }
-keep class com.google.android.gms.** { *; }

# Preserve native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep WebView JavaScript interface
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Preserve Capacitor plugin annotations
-keepattributes *Annotation*

# Keep plugin registration
-keep class * extends com.getcapacitor.Plugin {
    public <init>(...);
}

# Keep JSON serialization
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# Keep AWS Mobile Client
-keep class com.amazonaws.mobile.client.** { *; }
-keep class com.amazonaws.auth.** { *; }
