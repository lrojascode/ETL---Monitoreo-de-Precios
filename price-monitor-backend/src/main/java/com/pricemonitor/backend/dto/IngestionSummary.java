package com.pricemonitor.backend.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class IngestionSummary {
    private Integer processedCount;
    private Integer newProductsCount;
}
