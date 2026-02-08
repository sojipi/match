# 语言切换调试指南

## 问题描述
在设置页面切换语言没有效果

## 已实施的修复

### 1. 修复了 i18n 配置
- **文件**: `frontend/src/i18n/config.ts`
- **更改**:
  - 移除了 `Backend` 插件（不需要，因为我们直接导入翻译文件）
  - 禁用了 `useSuspense`（设置为 `false`）
  - 启用了 `debug` 模式（设置为 `true`）

### 2. 添加了 useTranslation Hook
- **文件**: `frontend/src/pages/SettingsPage.tsx`
- **更改**:
  - 导入了 `useTranslation` from 'react-i18next'
  - 在组件中使用 `const { t } = useTranslation()`
  - 更新了部分文本使用 `t()` 函数

### 3. 创建了语言测试组件
- **文件**: `frontend/src/components/LanguageTest.tsx`
- **功能**:
  - 显示当前语言
  - 显示翻译后的文本示例
  - 提供快速切换语言的按钮
  - 已添加到设置页面的"Language & Culture"标签页

## 测试步骤

### 1. 检查浏览器控制台
打开浏览器开发者工具（F12），查看控制台是否有 i18next 的调试信息：
- 应该看到类似 `i18next: languageChanged zh` 的消息
- 检查是否有任何错误信息

### 2. 检查 localStorage
在浏览器控制台中运行：
```javascript
localStorage.getItem('i18nextLng')
```
这应该显示当前选择的语言代码（如 'zh', 'en', 'es' 等）

### 3. 使用语言测试组件
1. 进入设置页面
2. 点击"Language & Culture"标签
3. 在页面顶部会看到"Language Test Component"
4. 点击不同的语言按钮（English, 中文, Español等）
5. 观察文本是否立即改变

### 4. 检查 LanguageSwitcher 组件
1. 在"Language & Culture"标签页中
2. 使用下拉菜单选择语言
3. 检查是否：
   - 下拉菜单的值改变了
   - localStorage 更新了
   - HTML lang 属性更新了

## 常见问题和解决方案

### 问题 1: 切换语言后页面没有更新
**原因**: 组件没有使用 `useTranslation` hook

**解决方案**: 
```typescript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
    const { t } = useTranslation();
    
    return <div>{t('common.welcome')}</div>;
};
```

### 问题 2: 翻译文件没有加载
**检查**:
1. 确认翻译文件存在且格式正确
2. 在浏览器控制台运行：
```javascript
import('./i18n/config').then(i18n => console.log(i18n.default.store.data))
```

### 问题 3: 语言切换后需要刷新页面
**原因**: 使用了 `useSuspense: true`

**解决方案**: 已在配置中设置为 `false`

### 问题 4: 某些页面显示英文，某些显示中文
**原因**: 部分组件使用了硬编码文本而不是翻译函数

**解决方案**: 需要逐个更新组件使用 `t()` 函数

## 需要更新的组件列表

以下组件可能需要更新以支持多语言：

### 高优先级（用户常访问的页面）
- [ ] `frontend/src/pages/Dashboard.tsx`
- [ ] `frontend/src/pages/MatchesPage.tsx`
- [ ] `frontend/src/pages/MessagesPage.tsx`
- [ ] `frontend/src/pages/ProfileManagementPage.tsx`
- [ ] `frontend/src/components/layout/AppLayout.tsx`

### 中优先级
- [ ] `frontend/src/pages/PersonalityAssessmentPage.tsx`
- [ ] `frontend/src/pages/AvatarPage.tsx`
- [ ] `frontend/src/pages/MatchDiscoveryPage.tsx`
- [ ] `frontend/src/pages/NotificationsPage.tsx`

### 低优先级
- [ ] `frontend/src/pages/CompatibilityReportPage.tsx`
- [ ] `frontend/src/pages/LiveMatchingTheaterPage.tsx`
- [ ] 其他辅助组件

## 更新组件的模板

```typescript
// 1. 导入 useTranslation
import { useTranslation } from 'react-i18next';

// 2. 在组件中使用
const MyComponent: React.FC = () => {
    const { t } = useTranslation();
    
    return (
        <div>
            {/* 替换硬编码文本 */}
            <h1>{t('navigation.dashboard')}</h1>
            <button>{t('common.save')}</button>
            <p>{t('common.loading')}</p>
        </div>
    );
};
```

## 验证语言切换是否工作

### 快速测试
1. 打开浏览器控制台
2. 运行以下代码：
```javascript
// 获取 i18n 实例
const i18n = window.i18n || document.querySelector('[data-i18n]')?.__i18n;

// 切换到中文
i18n?.changeLanguage('zh');

// 检查当前语言
console.log('Current language:', i18n?.language);

// 测试翻译
console.log('Welcome:', i18n?.t('common.welcome'));
```

### 完整测试流程
1. 清除 localStorage: `localStorage.clear()`
2. 刷新页面
3. 进入设置页面
4. 切换到中文
5. 检查：
   - 设置页面的标题是否变为"设置"
   - 标签页是否显示中文
   - 语言测试组件中的文本是否变为中文
6. 导航到其他页面，检查是否保持中文

## 调试命令

在浏览器控制台中运行这些命令来调试：

```javascript
// 1. 检查 i18n 是否初始化
console.log('i18n loaded:', !!window.i18next);

// 2. 检查当前语言
console.log('Current language:', localStorage.getItem('i18nextLng'));

// 3. 检查可用的翻译
console.log('Available translations:', Object.keys(window.i18next?.store?.data || {}));

// 4. 测试翻译函数
console.log('Test translation:', window.i18next?.t('common.welcome'));

// 5. 手动切换语言
window.i18next?.changeLanguage('zh').then(() => {
    console.log('Language changed to:', window.i18next.language);
});
```

## 下一步

如果语言测试组件工作正常，但其他页面仍然显示英文，那么需要：

1. 逐个更新页面组件添加 `useTranslation` hook
2. 将所有硬编码的文本替换为 `t()` 函数调用
3. 确保翻译键在所有语言文件中都存在

## 联系支持

如果问题仍然存在，请提供：
1. 浏览器控制台的完整输出
2. localStorage 中的 `i18nextLng` 值
3. 语言测试组件是否工作
4. 具体哪些页面/组件没有切换语言
