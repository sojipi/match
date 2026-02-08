# 多语言快速参考

## 🚀 快速开始

### 在组件中使用翻译

```typescript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
    const { t, i18n } = useTranslation();
    
    return (
        <div>
            {/* 基本使用 */}
            <h1>{t('common.welcome')}</h1>
            
            {/* 带参数 */}
            <p>{t('dashboard.welcome', { name: 'John' })}</p>
            
            {/* 当前语言 */}
            <span>Language: {i18n.language}</span>
            
            {/* 切换语言 */}
            <button onClick={() => i18n.changeLanguage('zh')}>
                中文
            </button>
        </div>
    );
};
```

## 📖 常用翻译键

### 通用 (common)
```typescript
t('common.welcome')      // 欢迎
t('common.loading')      // 加载中...
t('common.error')        // 错误
t('common.success')      // 成功
t('common.save')         // 保存
t('common.cancel')       // 取消
t('common.delete')       // 删除
t('common.edit')         // 编辑
t('common.back')         // 返回
t('common.next')         // 下一步
t('common.submit')       // 提交
t('common.close')        // 关闭
```

### 导航 (navigation)
```typescript
t('navigation.home')           // 首页
t('navigation.dashboard')      // 控制台
t('navigation.discover')       // 发现
t('navigation.matches')        // 匹配
t('navigation.messages')       // 消息
t('navigation.notifications')  // 通知
t('navigation.profile')        // 个人资料
t('navigation.settings')       // 设置
t('navigation.avatar')         // 我的化身
```

### 认证 (auth)
```typescript
t('auth.login')              // 登录
t('auth.logout')             // 退出
t('auth.register')           // 注册
t('auth.email')              // 电子邮箱
t('auth.password')           // 密码
t('auth.confirmPassword')    // 确认密码
t('auth.forgotPassword')     // 忘记密码？
```

### 匹配 (matching)
```typescript
t('matching.discover')           // 发现匹配
t('matching.compatibility')      // 兼容性
t('matching.compatibilityScore') // 兼容性评分
t('matching.like')               // 喜欢
t('matching.pass')               // 跳过
t('matching.superLike')          // 超级喜欢
t('matching.mutualMatch')        // 配对成功！
t('matching.startConversation')  // 开始对话
```

### 消息 (messages)
```typescript
t('messages.conversations')     // 对话
t('messages.newMessage')        // 新消息
t('messages.sendMessage')       // 发送消息
t('messages.typeMessage')       // 输入消息...
t('messages.online')            // 在线
t('messages.offline')           // 离线
```

### 设置 (settings)
```typescript
t('settings.title')              // 设置
t('settings.language')           // 语言
t('settings.theme')              // 主题
t('settings.accessibility')      // 无障碍
t('settings.privacy')            // 隐私
t('settings.culturalPreferences') // 文化偏好
```

## 🌍 支持的语言

| 代码 | 语言 | 本地名称 |
|------|------|----------|
| `en` | English | English |
| `zh` | Chinese | 中文 |
| `es` | Spanish | Español |
| `fr` | French | Français |
| `de` | German | Deutsch |
| `ja` | Japanese | 日本語 |

## 🔧 常用操作

### 切换语言
```typescript
const { i18n } = useTranslation();

// 切换到中文
i18n.changeLanguage('zh');

// 切换到英文
i18n.changeLanguage('en');
```

### 获取当前语言
```typescript
const { i18n } = useTranslation();
const currentLang = i18n.language; // 'zh', 'en', etc.
```

### 检查翻译是否存在
```typescript
const { i18n } = useTranslation();
const exists = i18n.exists('common.welcome'); // true/false
```

### 带参数的翻译
```typescript
// 翻译文件中: "welcome": "欢迎回来，{{name}}"
t('dashboard.welcome', { name: user.name })
// 输出: "欢迎回来，John"
```

## 🧪 测试语言切换

### 方法 1: 使用设置页面
1. 进入 `/settings`
2. 点击 "Language & Culture" 标签
3. 使用语言测试组件或下拉菜单

### 方法 2: 浏览器控制台
```javascript
// 切换到中文
window.i18next.changeLanguage('zh')

// 测试翻译
window.i18next.t('common.welcome')

// 查看当前语言
window.i18next.language
```

## 📝 添加新翻译

### 1. 在所有语言文件中添加键

**en/translation.json**
```json
{
    "myFeature": {
        "title": "My Feature",
        "description": "This is my feature"
    }
}
```

**zh/translation.json**
```json
{
    "myFeature": {
        "title": "我的功能",
        "description": "这是我的功能"
    }
}
```

### 2. 在组件中使用
```typescript
<h1>{t('myFeature.title')}</h1>
<p>{t('myFeature.description')}</p>
```

## ⚠️ 常见错误

### 错误 1: 显示翻译键而不是文本
```typescript
// ❌ 错误 - 显示 "common.welcome"
<h1>common.welcome</h1>

// ✅ 正确
<h1>{t('common.welcome')}</h1>
```

### 错误 2: 忘记导入 useTranslation
```typescript
// ❌ 错误
const MyComponent = () => {
    return <h1>{t('common.welcome')}</h1>; // t is not defined
};

// ✅ 正确
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
    const { t } = useTranslation();
    return <h1>{t('common.welcome')}</h1>;
};
```

### 错误 3: 翻译键不存在
```typescript
// ❌ 错误 - 键不存在
t('nonexistent.key') // 显示 "nonexistent.key"

// ✅ 正确 - 先在翻译文件中添加键
```

## 🎯 最佳实践

1. **使用命名空间**: 按功能组织翻译键
   ```typescript
   t('auth.login')
   t('profile.edit')
   t('messages.send')
   ```

2. **保持一致性**: 相同概念使用相同的键
   ```typescript
   // ✅ 好
   t('common.save')  // 在所有地方使用
   
   // ❌ 差
   t('common.save')
   t('profile.saveButton')
   t('settings.saveChanges')
   ```

3. **使用描述性名称**: 键名应该清楚表达含义
   ```typescript
   // ✅ 好
   t('auth.loginButton')
   t('profile.editPhotoButton')
   
   // ❌ 差
   t('btn1')
   t('text2')
   ```

4. **添加所有语言**: 新键必须在所有6种语言中添加
   ```
   ✅ en, zh, es, fr, de, ja 都有
   ❌ 只在 en 中添加
   ```

## 🔍 调试技巧

### 启用调试模式
在 `i18n/config.ts` 中:
```typescript
i18n.init({
    debug: true, // 在控制台显示调试信息
    // ...
});
```

### 检查翻译加载
```javascript
// 查看所有已加载的翻译
console.log(window.i18next.store.data);

// 查看特定语言的翻译
console.log(window.i18next.store.data.zh.translation);
```

### 监听语言变化
```typescript
const { i18n } = useTranslation();

useEffect(() => {
    const handleLanguageChange = (lng: string) => {
        console.log('Language changed to:', lng);
    };
    
    i18n.on('languageChanged', handleLanguageChange);
    
    return () => {
        i18n.off('languageChanged', handleLanguageChange);
    };
}, [i18n]);
```

## 📚 更多资源

- [i18next 官方文档](https://www.i18next.com/)
- [react-i18next 文档](https://react.i18next.com/)
- 项目文档: `LANGUAGE_SWITCHING_DEBUG.md`
- 完整实现: `I18N_IMPLEMENTATION_COMPLETE.md`

## 💡 提示

- 使用 `Ctrl+F` 在翻译文件中搜索键
- 保持翻译文件格式一致
- 定期检查所有语言的翻译完整性
- 测试每种语言的显示效果
- 考虑文本长度差异（某些语言更长）

---

**快速链接**:
- 设置页面: `/settings`
- 语言测试: 设置 → Language & Culture
- 翻译文件: `frontend/src/i18n/locales/`
