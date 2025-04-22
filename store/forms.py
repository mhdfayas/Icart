from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.Select(attrs={'class': 'form-select'}, 
                                  choices=[(5, '5 Stars - Excellent'), 
                                           (4, '4 Stars - Very Good'), 
                                           (3, '3 Stars - Good'), 
                                           (2, '2 Stars - Fair'), 
                                           (1, '1 Star - Poor')])
        }