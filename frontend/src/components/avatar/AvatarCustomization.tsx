/**
 * Avatar Customization Component
 */
import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    TextField,
    Button,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Slider,
    Alert,
    Chip,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress
} from '@mui/material';
import {
    Edit as EditIcon,
    Delete as DeleteIcon,
    Save as SaveIcon,
    Cancel as CancelIcon,
    Psychology as PsychologyIcon,
    Chat as ChatIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';

import { AIAvatar, AvatarCustomization as AvatarCustomizationType, AvatarCustomizationRequest } from '../../types/avatar';
import { avatarApi } from '../../services/avatarApi';

interface AvatarCustomizationProps {
    avatar: AIAvatar;
    onCustomizationApplied?: () => void;
}

interface CustomizationForm {
    customization_type: string;
    field_name: string;
    custom_value: any;
    reason: string;
}

const AvatarCustomization: React.FC<AvatarCustomizationProps> = ({ avatar, onCustomizationApplied }) => {
    const [customizations, setCustomizations] = useState<AvatarCustomizationType[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCustomizationDialog, setShowCustomizationDialog] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [form, setForm] = useState<CustomizationForm>({
        customization_type: '',
        field_name: '',
        custom_value: '',
        reason: ''
    });

    useEffect(() => {
        loadCustomizations();
    }, [avatar.id]);

    const loadCustomizations = async () => {
        try {
            setLoading(true);
            const data = await avatarApi.getAvatarCustomizations(avatar.id);
            setCustomizations(data);
        } catch (err: any) {
            setError('Failed to load customizations');
            console.error('Error loading customizations:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitCustomization = async () => {
        if (!form.customization_type || !form.field_name || form.custom_value === '') {
            setError('Please fill in all required fields');
            return;
        }

        try {
            setIsSubmitting(true);
            setError(null);

            const customizationRequest: AvatarCustomizationRequest = {
                customization_type: form.customization_type,
                field_name: form.field_name,
                custom_value: form.custom_value,
                reason: form.reason || undefined
            };

            await avatarApi.customizeAvatar(avatar.id, customizationRequest);

            // Reload customizations
            await loadCustomizations();

            // Close dialog and reset form
            setShowCustomizationDialog(false);
            setForm({
                customization_type: '',
                field_name: '',
                custom_value: '',
                reason: ''
            });

            if (onCustomizationApplied) {
                onCustomizationApplied();
            }
        } catch (err: any) {
            setError(err.message || 'Failed to apply customization');
            console.error('Error applying customization:', err);
        } finally {
            setIsSubmitting(false);
        }
    };

    const getCustomizationTypeOptions = () => [
        { value: 'personality_adjustment', label: 'Personality Adjustment' },
        { value: 'communication_style', label: 'Communication Style' },
        { value: 'response_style', label: 'Response Style' }
    ];

    const getFieldOptions = (customizationType: string) => {
        switch (customizationType) {
            case 'personality_adjustment':
                return [
                    { value: 'openness', label: 'Openness to Experience' },
                    { value: 'conscientiousness', label: 'Conscientiousness' },
                    { value: 'extraversion', label: 'Extraversion' },
                    { value: 'agreeableness', label: 'Agreeableness' },
                    { value: 'neuroticism', label: 'Neuroticism' }
                ];
            case 'communication_style':
                return [
                    { value: 'directness', label: 'Communication Directness' },
                    { value: 'formality', label: 'Formality Level' },
                    { value: 'humor_usage', label: 'Humor Usage' },
                    { value: 'listening_style', label: 'Listening Style' }
                ];
            case 'response_style':
                return [
                    { value: 'response_length', label: 'Response Length' },
                    { value: 'assertiveness', label: 'Assertiveness' },
                    { value: 'question_frequency', label: 'Question Frequency' }
                ];
            default:
                return [];
        }
    };

    const renderCustomValueInput = () => {
        const isPersonalityTrait = form.customization_type === 'personality_adjustment' &&
            ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'].includes(form.field_name);

        const isNumericField = isPersonalityTrait ||
            (form.customization_type === 'communication_style' && form.field_name === 'directness') ||
            (form.customization_type === 'response_style' && form.field_name === 'assertiveness');

        if (isNumericField) {
            return (
                <Box>
                    <Typography variant="body2" gutterBottom>
                        Value (0 = Low, 100 = High)
                    </Typography>
                    <Slider
                        value={typeof form.custom_value === 'number' ? form.custom_value * 100 : 50}
                        onChange={(_, value) => setForm({ ...form, custom_value: (value as number) / 100 })}
                        min={0}
                        max={100}
                        step={5}
                        marks={[
                            { value: 0, label: 'Low' },
                            { value: 50, label: 'Medium' },
                            { value: 100, label: 'High' }
                        ]}
                        valueLabelDisplay="on"
                        valueLabelFormat={(value) => `${value}%`}
                    />
                </Box>
            );
        }

        // For categorical fields
        const getCategoricalOptions = () => {
            if (form.customization_type === 'communication_style') {
                switch (form.field_name) {
                    case 'formality':
                        return ['casual', 'moderate', 'formal'];
                    case 'humor_usage':
                        return ['minimal', 'occasional', 'frequent_positive', 'witty_occasional'];
                    case 'listening_style':
                        return ['empathetic', 'analytical', 'interactive', 'balanced'];
                    default:
                        return [];
                }
            }
            if (form.customization_type === 'response_style') {
                switch (form.field_name) {
                    case 'response_length':
                        return ['concise', 'moderate', 'detailed', 'thorough'];
                    case 'question_frequency':
                        return ['occasional', 'moderate', 'frequent'];
                    default:
                        return [];
                }
            }
            return [];
        };

        const categoricalOptions = getCategoricalOptions();

        if (categoricalOptions.length > 0) {
            return (
                <FormControl fullWidth>
                    <InputLabel>Value</InputLabel>
                    <Select
                        value={form.custom_value}
                        onChange={(e) => setForm({ ...form, custom_value: e.target.value })}
                        label="Value"
                    >
                        {categoricalOptions.map((option) => (
                            <MenuItem key={option} value={option}>
                                {option.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            );
        }

        return (
            <TextField
                fullWidth
                label="Custom Value"
                value={form.custom_value}
                onChange={(e) => setForm({ ...form, custom_value: e.target.value })}
                placeholder="Enter your custom value"
            />
        );
    };

    const formatCustomValue = (customization: AvatarCustomizationType) => {
        if (typeof customization.custom_value === 'number') {
            if (customization.custom_value <= 1) {
                return `${Math.round(customization.custom_value * 100)}%`;
            }
            return customization.custom_value.toString();
        }
        if (typeof customization.custom_value === 'string') {
            return customization.custom_value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
        return String(customization.custom_value);
    };

    const getImpactColor = (impact: number) => {
        if (impact >= 0.7) return 'error';
        if (impact >= 0.4) return 'warning';
        return 'info';
    };

    const renderCustomizationDialog = () => (
        <Dialog
            open={showCustomizationDialog}
            onClose={() => setShowCustomizationDialog(false)}
            maxWidth="sm"
            fullWidth
        >
            <DialogTitle>
                Customize Your Avatar
            </DialogTitle>
            <DialogContent>
                <Box sx={{ pt: 1 }}>
                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <FormControl fullWidth>
                                <InputLabel>Customization Type</InputLabel>
                                <Select
                                    value={form.customization_type}
                                    onChange={(e) => setForm({
                                        ...form,
                                        customization_type: e.target.value,
                                        field_name: '',
                                        custom_value: ''
                                    })}
                                    label="Customization Type"
                                >
                                    {getCustomizationTypeOptions().map((option) => (
                                        <MenuItem key={option.value} value={option.value}>
                                            {option.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>

                        {form.customization_type && (
                            <Grid item xs={12}>
                                <FormControl fullWidth>
                                    <InputLabel>Field to Customize</InputLabel>
                                    <Select
                                        value={form.field_name}
                                        onChange={(e) => setForm({
                                            ...form,
                                            field_name: e.target.value,
                                            custom_value: ''
                                        })}
                                        label="Field to Customize"
                                    >
                                        {getFieldOptions(form.customization_type).map((option) => (
                                            <MenuItem key={option.value} value={option.value}>
                                                {option.label}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                        )}

                        {form.field_name && (
                            <Grid item xs={12}>
                                {renderCustomValueInput()}
                            </Grid>
                        )}

                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Reason (Optional)"
                                value={form.reason}
                                onChange={(e) => setForm({ ...form, reason: e.target.value })}
                                placeholder="Why are you making this change?"
                                multiline
                                rows={2}
                            />
                        </Grid>
                    </Grid>
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={() => setShowCustomizationDialog(false)}>
                    Cancel
                </Button>
                <Button
                    onClick={handleSubmitCustomization}
                    variant="contained"
                    disabled={isSubmitting || !form.customization_type || !form.field_name || form.custom_value === ''}
                    startIcon={isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />}
                >
                    {isSubmitting ? 'Applying...' : 'Apply Customization'}
                </Button>
            </DialogActions>
        </Dialog>
    );

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                    <Typography variant="h6" component="h2">
                        Avatar Customizations
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Fine-tune your avatar's personality and behavior
                    </Typography>
                </Box>
                <Button
                    variant="contained"
                    onClick={() => setShowCustomizationDialog(true)}
                    startIcon={<EditIcon />}
                >
                    Add Customization
                </Button>
            </Box>

            {/* Current Customizations */}
            {customizations.length === 0 ? (
                <Card>
                    <CardContent>
                        <Box textAlign="center" py={4}>
                            <SettingsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                            <Typography variant="h6" gutterBottom>
                                No Customizations Yet
                            </Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>
                                Your avatar is using the default personality configuration.
                                Add customizations to make it more uniquely yours.
                            </Typography>
                            <Button
                                variant="outlined"
                                onClick={() => setShowCustomizationDialog(true)}
                                startIcon={<EditIcon />}
                            >
                                Add First Customization
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            ) : (
                <Grid container spacing={2}>
                    {customizations.map((customization) => (
                        <Grid item xs={12} key={customization.id}>
                            <Card>
                                <CardContent>
                                    <Box display="flex" alignItems="flex-start" gap={2}>
                                        <Box sx={{ mt: 0.5 }}>
                                            {customization.customization_type === 'personality_adjustment' && <PsychologyIcon color="primary" />}
                                            {customization.customization_type === 'communication_style' && <ChatIcon color="primary" />}
                                            {customization.customization_type === 'response_style' && <SettingsIcon color="primary" />}
                                        </Box>

                                        <Box sx={{ flexGrow: 1 }}>
                                            <Box display="flex" alignItems="center" gap={1} mb={1}>
                                                <Typography variant="subtitle1" fontWeight="medium">
                                                    {customization.field_name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                                </Typography>
                                                <Chip
                                                    label={customization.customization_type.replace('_', ' ')}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                                <Chip
                                                    label={`Impact: ${Math.round(customization.impact_score * 100)}%`}
                                                    size="small"
                                                    color={getImpactColor(customization.impact_score) as any}
                                                    variant="outlined"
                                                />
                                            </Box>

                                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                                <strong>Original:</strong> {formatCustomValue({ ...customization, custom_value: customization.original_value })} →{' '}
                                                <strong>Custom:</strong> {formatCustomValue(customization)}
                                            </Typography>

                                            {customization.reason && (
                                                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                                    "{customization.reason}"
                                                </Typography>
                                            )}

                                            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                                Applied on {new Date(customization.created_at).toLocaleDateString()}
                                            </Typography>
                                        </Box>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {renderCustomizationDialog()}
        </Box>
    );
};

export default AvatarCustomization;